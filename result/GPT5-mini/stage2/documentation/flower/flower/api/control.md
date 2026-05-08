# `control.py`

## `flower.api.control.ControlHandler` · *class*

## Summary:
ControlHandler is a minimal API request handler mixin for control-oriented endpoints that provides two small helper methods used by control routes: is_worker (to check worker membership) and error_reason (to extract a worker-specific error message from a broadcast response).

## Description:
ControlHandler is intended to be subclassed (or registered directly) as a Tornado request handler for control API routes within the Flower application. It does not override request lifecycle behavior itself; it relies on the BaseApiHandler behavior (authentication, error formatting, per-request instantiation by Tornado). Typical callers are the control-related request handlers in the Flower web UI that need to:
- verify whether a worker name refers to a known worker, and
- extract an error string for a particular worker from a control/broadcast response structure.

This class exists to centralize small, reusable control-related utilities so handler implementations do not duplicate membership checks and response-parsing logic.

## State:
This class defines no persistent attributes of its own. It relies on inherited state and module-level variables:

- self.application (inherited from Tornado RequestHandler / BaseApiHandler)
  - Expected to expose application.workers, a membership collection mapping or set whose keys are worker names (strings). The exact container type is not enforced by ControlHandler, but membership testing (workername in application.workers) must be supported.
- logger (module-level)
  - ControlHandler calls logger.error(...) when it cannot extract an error reason from the provided response structure. The existence of a module-level logger variable named logger is assumed by the implementation.

Class invariants:
- No instance attributes are created by ControlHandler. It assumes that self.application exists and that self.application.workers is accessible at the time is_worker is called.
- Methods do not mutate shared state.

## Lifecycle:
Creation:
- ControlHandler has no custom __init__. Instances are created by Tornado when a route references this handler class (see BaseApiHandler documentation for per-request instantiation details).

Usage:
- Typical usage is per-request: Tornado instantiates the handler, then application code invokes the handler's HTTP method (get/post/...) which may call is_worker() and error_reason() as helpers.
- There is no required call ordering between the two methods; they are independent utilities.
- Example typical flow:
  1. A control API handler receives a request.
  2. It calls is_worker(workername) to verify the worker is known before issuing control commands.
  3. If a broadcast/remote control call returns a response aggregation, the handler calls error_reason(workername, response) to extract a human-readable error message for that worker (if any).

Destruction:
- No cleanup is required by ControlHandler itself. Tornado discards the handler instance after the request finishes.

## Method Map:
graph LR
    A[External code / HTTP method] --> B[is_worker(workername)]
    A --> C[error_reason(workername, response)]
    C --> D[module-level logger.error(...) on failure]

## Methods (behavioral details)

- is_worker(workername)
  - Purpose: Determine whether the provided workername refers to a known worker.
  - Args:
      workername (str | any falsy): Candidate worker identifier. Commonly a string; may be None or empty string.
  - Returns:
      - If workername is truthy:
          - Returns True if workername is present in self.application.workers.
          - Returns False if workername is not present in self.application.workers.
      - If workername is falsy (e.g., None or empty string):
          - Returns the original falsy workername value (e.g., None or '').
    Note: The implementation uses Python's "and" expression (workername and (workername in self.application.workers)), so the exact return value when workername is falsy is that original falsy object rather than the boolean False.
  - Side effects: None.
  - Exceptions: None raised by this method itself (assuming self.application and self.application.workers exist). If self.application or self.application.workers is missing, attribute access will raise AttributeError.

- error_reason(workername, response)
  - Purpose: Extract a worker-specific error message from an aggregation/broadcast response structure produced by control operations.
  - Args:
      workername (str): Worker identifier to look up in the response entries.
      response (iterable): An iterable (commonly a list or tuple) of mapping-like entries. Each entry is expected to be a mapping where the key is a worker name and the value is a mapping containing at least an 'error' key (or not).
  - Returns:
      - If any entry in response contains the workername as a key, returns that entry's value.get('error', 'Unknown reason').
        * That returned value may be any object stored under 'error' (commonly a string). If the 'error' key is absent, the string 'Unknown reason' is returned.
      - If no entries contain the workername key, logs an error and returns the string 'Unknown reason'.
  - Side effects:
      - If no entry contains workername, calls logger.error("Failed to extract error reason from '%s'", response).
  - Edge cases and error conditions:
      - If an entry that contains workername maps to a non-mapping object (i.e., value lacks a .get method), calling .get will raise AttributeError; this is not caught and will propagate.
      - If response is not iterable or its elements are not subscriptable mappings, the code may raise TypeError or KeyError in places; only KeyError from res[workername] is caught and ignored to continue searching.
      - The function intentionally ignores KeyError for missing worker keys to allow scanning subsequent entries.

## Raises:
- __init__: ControlHandler declares no __init__ and therefore raises no new exceptions itself during construction beyond those that may arise from the Tornado/BaseApiHandler initialization (see BaseApiHandler documentation for request-initialization errors).
- is_worker:
  - May raise AttributeError if self.application or self.application.workers is not present.
- error_reason:
  - Does not explicitly raise for missing keys (KeyError is caught and ignored for res[workername]), but may raise:
      - AttributeError if a found res[workername] value does not support .get(...)
      - TypeError or other exceptions if response is not iterable or its elements are not mappings
    These exceptions are not caught within error_reason and will propagate to the caller.

## Example (usage scenario):
- Context: inside a control HTTP method handler (per-request handler instance)
  1. Check membership:
     - Call is_worker('worker@example.com').
     - If the result is truthy (True), proceed to send a control command.
     - If the result is falsy (False, None, or ''), respond with an appropriate client error.
  2. After issuing a broadcast control command, you receive an aggregated response (commonly a list of dicts where each dict maps workername -> result-dict). To get a user-friendly error:
     - Call error_reason('worker@example.com', response).
     - Use the returned string as the message shown to the user or included in an API error payload.
  3. No explicit cleanup is needed for these helper calls.

## Cross-references:
- See BaseApiHandler for per-request instantiation, authentication enforcement, and write_error behavior.
- Consumers should ensure response argument shape matches expectations (iterable of mappings) to avoid unexpected exceptions.

### `flower.api.control.ControlHandler.is_worker` · *method*

## Summary:
Perform a short-circuit membership check: return the original falsy workername if it is falsy; otherwise return the result of testing membership of workername in the application's workers collection. The method does not modify object state.

## Description:
- Callers: Not referenced elsewhere within this module's visible code. It is a helper method on ControlHandler meant to evaluate whether a given worker identifier exists in the application's worker registry.
- Behavior rationale: The method implements the two-step pattern "value provided && value present in registry" using Python's short-circuit "and" expression, keeping the check compact and avoiding repeated logic in callers.

## Args:
    workername (Any): Candidate worker identifier. The method accepts any Python object; typical runtime values are strings (worker names) or None when a value is missing.

## Returns:
    Any:
    - If workername is falsy (for example None, '', 0, False), the method returns that original falsy value immediately (Python's "and" returns the first falsy operand).
    - If workername is truthy, the method returns the result of the expression (workername in self.application.workers). For built-in containers this will be a boolean True or False; for custom containers it may be any truthy/falsy value returned by their __contains__ implementation.
    - Therefore the return value is either the original falsy workername or the membership-test result.

## Raises:
    - AttributeError: if self.application has no attribute 'workers' (accessing self.application.workers).
    - TypeError: if the membership operation "workername in self.application.workers" is not supported for the provided workername or for the workers object.
    Note: The method itself contains no explicit raise statements; these exceptions are implicit from attribute access or the membership test.

## State Changes:
- Attributes READ:
    - self.application
    - self.application.workers
- Attributes WRITTEN:
    - None — no attributes on self or self.application are modified.

## Constraints:
- Preconditions:
    - self.application must be accessible from the handler instance.
    - self.application.workers must be a container-like object that supports the "in" membership test.
- Postconditions:
    - No mutation of self or application state occurs.
    - The return value reflects the short-circuit semantics described above.

## Side Effects and Usage guidance:
- Side effects: None — no I/O, network calls, or external state mutations.
- Usage guidance:
    - Callers that require a strict boolean result should coerce the return value to bool (for example by applying the built-in bool() to the method's return).
    - Be aware that falsy inputs are returned unchanged; if callers simply use the return value in a conditional, that will treat falsy original inputs as False-like without distinction.

### `flower.api.control.ControlHandler.error_reason` · *method*

## Summary:
Returns the first available value stored under the 'error' key for a given worker from an iterable of response mappings; if none is found, logs an error and returns the default string 'Unknown reason'.

## Description:
This utility extracts a worker-specific error entry from a sequence of response objects produced by control/inspection operations. It iterates the provided response iterable in order and, for the first element that contains the requested worker, returns that element's mapping.get('error', 'Unknown reason') result.

Known callers and lifecycle stage:
- Used inside ControlHandler when assembling worker status or error information for HTTP responses or UI views. It runs during request/response processing after control operations return their combined results.

Why this logic is a separate method:
- Encapsulates the repeated pattern of scanning multiple response fragments, handling missing worker keys, defaulting missing 'error' entries, and logging a failure when no data is found. Separating it keeps request handling code concise and makes the extraction behavior testable.

## Args:
    workername (hashable, typically str): Key used to access per-worker entries inside each response element. Must be appropriate for the mapping types contained in response.
    response (Iterable[Mapping]): An iterable (commonly a list or tuple) of mapping-like objects. Each mapping is expected to support subscription with workername (e.g., res[workername]) and the resulting value is expected to be a mapping-like object with a .get method.

## Returns:
    Any: The value returned by the first matching element's .get('error', 'Unknown reason').
    - If a matching element exists and its worker-mapping contains an 'error' key, that value is returned (type is not enforced by this method and may be str or any other type).
    - If a matching element exists but has no 'error' key, the mapping.get call will return the default string 'Unknown reason'.
    - If no response element contains the workername key, the method logs an error and returns the string 'Unknown reason'.

## Raises:
    - The method intentionally catches KeyError raised by res[workername] and continues to the next element.
    - Other exceptions may propagate to the caller:
        - TypeError: If `response` is not iterable, or if an element does not support subscription with workername.
        - AttributeError: If res[workername] exists but is not a mapping-like object (i.e., has no .get method), calling .get will raise AttributeError.
        - IndexError: May occur if an element is an indexable sequence and workername is an integer out of range.
    The method does not raise exceptions itself aside from allowing these runtime errors to bubble up.

## State Changes:
    Attributes READ:
        - None (does not read any self.<attr> attributes)
    Attributes WRITTEN:
        - None (does not modify any self.<attr> attributes)

## Constraints:
    Preconditions:
        - `response` should be an iterable of mappings or mapping-like objects.
        - `workername` should be a valid key for those mappings.
    Postconditions:
        - Returns the first found error value or the default 'Unknown reason'.
        - If no worker entry was found in any element, an error is logged via the module-level logger and the method returns 'Unknown reason'.

## Side Effects:
    - Emits an error-level log via the module-level logger variable (calls logger.error(...)) when no error reason could be extracted from any element in response.
    - Does not perform network I/O or mutate the provided response elements or any self attributes.

## Example:
    Given response = [{'hostA': {'error': 'out of memory'}}, {'hostB': {'error': 'timeout'}}]
    Calling error_reason('hostA', response) returns 'out of memory'.
    If no element contains 'hostC' the method logs an error and returns 'Unknown reason'.

## `flower.api.control.WorkerShutDown` · *class*

## Summary:
Handler for HTTP POST requests that instructs a specific worker to shut down; verifies worker existence, broadcasts a 'shutdown' control command to the targeted worker, and returns a confirmation message to the client.

## Description:
WorkerShutDown is a Tornado request handler (subclass of ControlHandler) intended to be mounted at a route that includes a worker identifier (workername) and invoked via HTTP POST. Typical callers are the Flower web UI or API clients that need to remotely request a worker process to terminate.

This handler:
- Ensures the requesting client is authenticated (decorated with Tornado's web.authenticated).
- Validates that the provided workername refers to a known worker using ControlHandler.is_worker.
- Uses the application's Celery-like control interface (self.capp.control.broadcast) to send a 'shutdown' command targeted only to the named worker.
- Writes a short JSON-like confirmation payload to the HTTP response.

Reason for a distinct class:
- Encapsulates a single control action (shutdown) with validation and response behavior suitable for a RESTful POST endpoint.
- Keeps control-route implementations small and focused; reuses ControlHandler helpers.

Known callers / instantiation sites:
- Registered as a Tornado request handler in the Flower web application routing table (per-request instantiation by Tornado).
- Invoked when an authenticated client performs an HTTP POST against the shutdown route for a worker (e.g., POST /api/workers/{workername}/shutdown).

## State:
This class defines no new instance attributes. It relies on inherited/module-level state:

- self.application (inherited from Tornado RequestHandler / BaseApiHandler)
  - Expected: exposes application.workers (a collection supporting membership tests) so ControlHandler.is_worker can validate worker membership.
- self.capp
  - Expected: application-level Celery or Celery-like app object available on the handler instance, exposing a .control attribute with a .broadcast(command, destination=[...]) method.
  - Usage here: self.capp.control.broadcast('shutdown', destination=[workername])
- logger (module-level)
  - Used to log the shutdown action: logger.info("Shutting down '%s' worker", workername)
- No persistent attributes are introduced by WorkerShutDown itself.

Valid values / invariants:
- workername: expected to be a non-empty string identifying a worker known to self.application.workers.
- Class invariant: methods do not mutate global state; they rely on the presence of self.application and self.capp for correct operation.

## Lifecycle:
Creation:
- Instantiated by Tornado for each incoming HTTP request that matches the route bound to this handler.
- No constructor arguments beyond what Tornado provides; no factory methods.

Usage (typical flow for a POST request):
1. Tornado instantiates the handler and invokes post(self, workername) with workername extracted from the route.
2. Authentication is enforced by web.authenticated before entering post; if not authenticated Tornado's authentication behavior applies (redirect or HTTP error).
3. post calls self.is_worker(workername) to validate membership.
   - If validation fails (is_worker returns falsy), post raises web.HTTPError(404, ...).
4. On success, post logs an informational message, broadcasts the 'shutdown' command targeted to the worker, and writes a confirmation payload to the response body.
5. The handler instance is discarded by Tornado after request completion; no explicit cleanup required.

Destruction:
- No cleanup, closing, or context-manager behavior required by this class.

Sequencing constraints:
- post must first validate membership (is_worker) before broadcasting; the implementation enforces that ordering.
- There is no async/await behavior in the method; if broadcast is blocking or raises, that behavior is propagated to Tornado's request lifecycle.

## Method Map:
graph LR
    A[HTTP POST request -> WorkerShutDown.post(workername)] --> B{web.authenticated}
    B -->|authenticated| C[is_worker(workername)]
    C -->|false| D[raise web.HTTPError(404, "Unknown worker '...'")]
    C -->|true| E[logger.info("Shutting down '%s' worker", workername)]
    E --> F[self.capp.control.broadcast('shutdown', destination=[workername])]
    F --> G[self.write({"message": "Shutting down!"})]
    B -->|unauthenticated| H[Tornado authentication handling (redirect / HTTPError)]

## Raises:
- web.HTTPError(404, f"Unknown worker '{workername}'")
  - Trigger: self.is_worker(workername) is falsy (worker unknown or workername invalid/empty).
- Exceptions propagated from lower layers:
  - AttributeError: if expected attributes are missing (e.g., self.capp or self.capp.control is not present, or self.is_worker is absent) — indicates misconfiguration or that the handler was not instantiated with the expected application state.
  - Any exception raised by self.capp.control.broadcast (network errors, Celery exceptions, etc.) will propagate and result in a 500-level response unless caught by upstream error handlers.
  - Tornado authentication behavior: web.authenticated will enforce authentication; failure may cause a redirect or an HTTP error (not raised directly by post but occurring before execution).

Edge cases:
- If workername is falsy (None or empty string), ControlHandler.is_worker will return a falsy value; post will treat that as "unknown" and raise the 404 HTTPError.
- If the control broadcast succeeds but the targeted worker ignores the shutdown or fails to shut down, this handler only issues the command and returns confirmation; it does not verify successful termination.
- The exact serialization of the written dict depends on Tornado/BaseApiHandler (commonly JSON).

## Example (usage scenario):
- An authenticated API client issues a POST to the shutdown endpoint for a worker (route contains the workername).
- Tornado invokes WorkerShutDown.post with the workername extracted from the URL.
- The handler checks membership; if the worker is unknown, it responds with HTTP 404 and an error message.
- If known, the handler logs the intent, broadcasts the 'shutdown' command targeted to that worker via self.capp.control.broadcast, and responds with a short confirmation payload (written as a dict with the message "Shutting down!").
- No further action is required from the client; the actual shutdown is performed by the remote worker process in response to the broadcast.

### `flower.api.control.WorkerShutDown.post` · *method*

## Summary:
Sends a Celery control "shutdown" broadcast targeted at the given worker and returns a short JSON confirmation; does not mutate handler instance state.

## Description:
This method is the HTTP POST handler invoked by Tornado when a client issues a POST request to the route handled by WorkerShutDown. It runs as part of the per-request Tornado handler lifecycle and is executed after authentication (the WorkerShutDown handler is decorated with web.authenticated in its class declaration).

Known callers and invocation context:
- Tornado's request-dispatch machinery calls this method when an authenticated client makes a POST request mapped to the WorkerShutDown handler.
- Typical callers are UI code or API clients that request a remote worker shutdown via the Flower control API.
- The method is intentionally a request handler because it represents a networked HTTP endpoint and must perform request-scoped actions (authentication, request/response I/O, and issuing a control command). Keeping the logic here keeps endpoint semantics (auth, validation, control broadcast, and response formatting) localized and uses shared helper methods (is_worker) from ControlHandler.

## Args:
    workername (str):
        Identifier for the target worker. Expected to be the worker name as used by the application (commonly a string).
        - Allowed values: any object acceptable to ControlHandler.is_worker (typically a non-empty string).
        - If workername is falsy (e.g., None or empty string), ControlHandler.is_worker will return that falsy value; post will treat this as "not a known worker" and raise HTTP 404.

## Returns:
    None
    - The method writes an HTTP response body and returns None (typical Tornado RequestHandler behavior).
    - On success, it writes a JSON-like dictionary: {"message": "Shutting down!"} to the response body (via self.write).
    - There is no explicit return value; the observable effect is the HTTP response and the side-effect broadcast.

## Raises:
    tornado.web.HTTPError:
        - Raised with status 404 and message "Unknown worker '<workername>'" exactly when ControlHandler.is_worker(workername) evaluates to a falsy value (meaning the worker is not known).
        - Caller-visible: results in an HTTP 404 response with that reason text (Tornado converts the HTTPError into an HTTP response).
    AttributeError / TypeError (possible, not explicit):
        - If required attributes are missing or have unexpected types (for example, if self.capp or self.capp.control does not exist or does not provide a broadcast method), attribute access or the broadcast call may raise AttributeError or TypeError. These are not explicitly caught in this method and will propagate.

## State Changes:
Attributes READ:
    self.is_worker (method) - used to check membership of workername (indirectly reads self.application.workers).
    self.capp (attribute) - accessed to reach self.capp.control.broadcast.
    self.capp.control (attribute) - used to call broadcast; read to perform control action.
    self.write (method) - used to write the response body.
    module-level logger (logger.info) - used for informational logging (module-level, not an instance attribute).

Attributes WRITTEN:
    None — this method does not mutate any self.<attr> fields on the handler instance.

Note: is_worker internally reads self.application.workers; that is an indirect read performed via the call to self.is_worker.

## Constraints:
Preconditions:
    - The handler instance must have a callable is_worker method (provided by ControlHandler).
    - self.capp must be present and expose control.broadcast(destination=[...]) as a callable.
    - The request should be authenticated (the handler class is decorated with web.authenticated); Tornado will enforce this before invoking post.

Postconditions:
    - If the method returns normally (no exception raised), a control broadcast for action 'shutdown' was issued with destination set to a single-element list containing the supplied workername.
    - A JSON-like HTTP response body containing {"message": "Shutting down!"} has been written to the response (via self.write).
    - The handler instance remains unchanged (no new or modified instance attributes).

## Side Effects:
    - Network/IPC: Calls self.capp.control.broadcast('shutdown', destination=[workername]) which sends a shutdown control message to the target worker(s). This is an external control/action that may result in the remote worker process terminating.
    - HTTP response I/O: Calls self.write(...) to emit a JSON-like response to the client.
    - Logging: Emits an informational log entry via the module-level logger (logger.info("Shutting down '%s' worker", workername)).
    - No cleanup or synchronous blocking behavior is performed by this method itself; the broadcast is invoked and the method returns after writing the response.

## Implementation notes / edge cases:
    - Because ControlHandler.is_worker returns the original falsy value when workername is falsy, passing None or '' will cause the 404 path to trigger with the message Unknown worker 'None' or Unknown worker ''. Callers should validate workername if they want different behavior.
    - The method does not inspect or wait for any acknowledgement from the broadcast; it only issues the broadcast and responds to the HTTP client immediately.
    - If self.capp.control.broadcast raises an exception, that exception will propagate and typically result in a 500 error unless caught by higher-level Tornado error handlers.

## `flower.api.control.WorkerPoolRestart` · *class*

## Summary:
WorkerPoolRestart is an authenticated HTTP POST request handler that triggers a pool restart on a single named worker by broadcasting a 'pool_restart' control command and returning a success or failure message to the client.

## Description:
This Tornado request handler is used by the Flower control API to restart a worker's execution pool (without reloading the worker process). It should be instantiated by Tornado when a route for restarting a worker's pool is registered (typical route: POST /api/workers/{workername}/pool/restart). The method is decorated with Tornado's @web.authenticated, so requests must be authenticated according to the application's authentication policy.

Typical callers/factories:
- Tornado application route registration that maps an HTTP POST endpoint to WorkerPoolRestart.
- UI or API clients that perform an authenticated POST request to the worker pool restart endpoint.

Motivation and responsibilities:
- Encapsulates the control flow for requesting a pool restart on exactly one worker.
- Performs worker existence validation, issues the control broadcast specific to a single worker, interprets the aggregated response, and produces appropriate HTTP-level responses (success status message or 403 with a textual error).
- Relies on inherited helper utilities (ControlHandler.is_worker and ControlHandler.error_reason) and the application's Celery application bridge available at self.capp.

## State:
This class does not declare its own persistent attributes. It relies on inherited/request-scoped attributes made available by Tornado/BaseApiHandler/ControlHandler:

- self.application (provided by Tornado RequestHandler)
  - Expected: exposes application.workers, a container supporting membership testing (workername in application.workers).
  - Invariant: application.workers must be accessible when post(...) is called.

- self.capp (inherited / provided by surrounding application context)
  - Type: an application object exposing a control API with a broadcast method.
  - Expected method signature (semantically):
      broadcast(command: str,
                arguments: dict | None = None,
                destination: list[str] | None = None,
                reply: bool = True) -> list[dict] | None
  - Expected return shape: an iterable (commonly a list) of mapping-like entries where each entry maps worker name -> result-dict (e.g. {'worker@example.com': {'ok': True}} or {'worker@example.com': {'error': 'reason'}}).

- logger (module-level logging.Logger)
  - Used for informational and error logging. Must exist at module scope as referenced by the handler.

Class invariants:
- No instance attributes are created by WorkerPoolRestart.
- The handler assumes self.capp and self.application exist and are well-formed at request time.
- The handler does not mutate application state.

## Lifecycle:
Creation:
- No custom constructor. Instances are created per-request by Tornado when the route is invoked.
- No required constructor arguments beyond what Tornado provides when instantiating request handlers.

Usage:
- Method sequence and responsibilities:
    1. Tornado receives an authenticated POST request routed to WorkerPoolRestart.post with the captured path parameter workername.
    2. post checks worker membership via self.is_worker(workername).
    3. If the worker exists, the handler calls self.capp.control.broadcast(...) with command 'pool_restart', arguments {'reload': False}, destination set to a single-element list [workername], and reply=True to collect results.
    4. The handler examines the broadcast response. If the response indicates an 'ok' result for that worker, it writes a JSON-serializable dict message confirming restart. Otherwise, it logs the response, sets HTTP status 403, extracts a human-friendly reason via self.error_reason(workername, response), and writes a failure message string back to the client.

- Authentication: Because of @web.authenticated, the authenticated check runs before post executes; ensure Tornado authentication setup is configured.

Destruction:
- No cleanup responsibilities. Tornado discards the handler after the request completes.

Sequencing constraints:
- post must only be called in the context of a Tornado request; callers must pass a valid workername path parameter.
- self.capp.control.broadcast should be available and callable; otherwise attribute access will raise exceptions.

## Method Map:
graph LR
    A[Incoming authenticated HTTP POST(workername)] --> B[is_worker(workername)]
    B --> |not found| C[raise web.HTTPError(404)]
    B --> |found| D[capp.control.broadcast('pool_restart', arguments={'reload':False}, destination=[workername], reply=True)]
    D --> E[response evaluation]
    E --> |response and 'ok' in response[0][workername]| F[write({"message": "Restarting 'worker' worker's pool"})]
    E --> |otherwise| G[logger.error(response) -> set_status(403) -> reason = error_reason(workername,response) -> write(f"Failed...: {reason}")]

## Behavior of post(self, workername)
- Inputs:
    - workername (str): Worker identifier extracted from the URL/path. Must be a non-empty string representing a known worker.

- Side effects:
    - Calls self.capp.control.broadcast(...) to request the pool restart on the worker.
    - May log messages via module-level logger.
    - Writes an HTTP response body via self.write(...) and may change the HTTP status via self.set_status(...).

- Return / Response behavior:
    - Success path:
        - Condition: response is truthy AND response[0][workername] contains the key 'ok'.
        - Action: respond with a JSON-serializable dict: {"message": "Restarting '{workername}' worker's pool"} and leave default HTTP status (200).
    - Failure path:
        - Condition: any other case where the presence of 'ok' cannot be confirmed.
        - Action: log the raw response, set HTTP status to 403, compute reason = self.error_reason(workername, response), and write the textual failure message:
            "Failed to restart the '{workername}' pool: {reason}"

- Important note on response shape and edge cases:
    - The code expects response to be an iterable with at least one entry (response[0]) that is a mapping containing workername as a key mapped to a mapping-like result. Typical success response: [{'worker1': {'ok': True}}]. Typical failure response: [{'worker1': {'error': 'some message'}}].
    - If response is None or an empty list, the truthiness guard will be False and the handler will go to the failure path (403) and call error_reason(...), which will in turn log and return 'Unknown reason' as described by ControlHandler.error_reason.
    - If response is truthy but response[0] does not contain workername, accessing response[0][workername] will raise KeyError and propagate as a server error (500) because the handler does not catch this exception. Similarly, if response[0][workername] exists but is not a mapping (lacks membership checking for 'ok'), attempting to test 'ok' in that object may raise a TypeError or AttributeError; such exceptions will propagate unless handled by higher-level Tornado error handlers.
    - Therefore, callers and the control.broadcast implementation should ensure consistent return shapes to avoid server-side exceptions.

## Raises:
- web.HTTPError(404): raised immediately by post when is_worker(workername) returns a falsy value (worker not known). The handler constructs the message: "Unknown worker '{workername}'".
- Possible unhandled exceptions (propagate to Tornado error handling):
    - KeyError: if response[0] does not contain workername and response is truthy.
    - TypeError / AttributeError: if the returned response elements are not mapping-like or the expected keys are missing in unexpected ways.
- __init__: This class defines no __init__; any exceptions during construction would come from Tornado/BaseApiHandler initialization (not from WorkerPoolRestart itself).

## Example:
- Route registration (conceptual):
  - Register a POST route such as /api/workers/{workername}/pool/restart -> WorkerPoolRestart

- Successful operation scenario:
  1. Client issues an authenticated POST to /api/workers/worker1/pool/restart.
  2. post('worker1') checks self.is_worker('worker1') -> True.
  3. Calls self.capp.control.broadcast('pool_restart', arguments={'reload': False}, destination=['worker1'], reply=True).
  4. Suppose broadcast returns: [{'worker1': {'ok': True}}]
  5. Handler responds with status 200 and body: {"message": "Restarting 'worker1' worker's pool"}

- Failure operation scenario (control error):
  1. Broadcast returns: [{'worker1': {'error': 'could not restart pool: busy'}}]
  2. Handler logs the raw response, sets HTTP status to 403, computes reason via error_reason('worker1', response) -> "could not restart pool: busy", and writes:
     "Failed to restart the 'worker1' pool: could not restart pool: busy"

- Malformed response caution:
  - If broadcast returns a non-standard structure (e.g., [{'otherworker': {'ok': True}}] or an object that is not mapping-like), the handler may raise KeyError or TypeError; ensure the control layer returns the expected shape.

### `flower.api.control.WorkerPoolRestart.post` · *method*

## Summary:
Sends a pool-restart control command for a given worker via the application control API and writes an HTTP response that communicates whether the restart command was accepted or failed; it logs the attempt and may set a 403 status on failure.

## Description:
This method is the Tornado HTTP POST handler for restarting a single worker's pool. It is called by the Tornado request lifecycle when an authenticated client issues a POST to the WorkerPoolRestart endpoint (the method is decorated with web.authenticated). The method is separated into its own handler because it combines HTTP-level concerns (request validation, status codes, response writing) with issuing an external control command (self.capp.control.broadcast) and interpreting its reply; keeping these steps together localizes the request->control->response flow.

Known callers / invocation context:
- Tornado framework: invoked as the POST handler for the worker pool restart route, after authentication has been enforced by the decorator.

Why this logic is its own method:
- It must validate the worker identifier, call an external control API with specific arguments, inspect the structured reply, log results, and produce an appropriate HTTP response. These responsibilities cross boundary layers (HTTP, application control, logging), so they belong in a focused handler method.

## Args:
    workername (str): The name/identifier of the target worker to restart. Required. Must be recognized by the handler's self.is_worker(workername) method.

## Returns:
    None
    - The handler does not return a Python value; it writes to the HTTP response stream via self.write(...) and may change the HTTP status via self.set_status(...).
    - Success case: writes a JSON-serializable dict with a "message" key (e.g. {"message": "Restarting 'worker1' worker's pool"}) and leaves the HTTP status at the default (200).
    - Failure case: sets the HTTP status to 403 and writes a plain-text error string (e.g. "Failed to restart the 'worker1' pool: <reason>").

Example response bodies:
    - Success (body written via self.write(dict(...))):
        {"message": "Restarting 'worker1' worker's pool"}
    - Failure (plain string written via self.write(...)):
        "Failed to restart the 'worker1' pool: <reason>"

## Raises:
    web.HTTPError(404): If self.is_worker(workername) returns False — the workername is unknown.
    KeyError / IndexError / TypeError: If the response returned by self.capp.control.broadcast does not have the expected sequence/dictionary structure, attempts to index response[0] or access response[0][workername] or check 'ok' membership may raise these exceptions. These exceptions are not caught inside the method.

## Behavior and expected external contract:
- The method calls:
    self.capp.control.broadcast(
        'pool_restart',
        arguments={'reload': False},
        destination=[workername],
        reply=True
    )
  It expects the broadcast to return a truthy sequence (commonly a list) whose first element is a mapping where the key workername maps to a dictionary containing an 'ok' key on success.
- Success condition (as evaluated by this method):
    - response is truthy, and
    - response[0][workername] contains the key 'ok' (membership checked via 'ok' in response[0][workername]).
- Failure conditions handled by the method:
    - response is falsy (e.g., empty list or None), or
    - response[0] does not contain workername, or
    - response[0][workername] does not contain the 'ok' key.
  In these handled failure cases, the method logs the raw response, sets HTTP status 403, obtains a human-readable reason via self.error_reason(workername, response), and writes a failure string to the response body.

## State Changes:
Attributes READ:
    - self.is_worker (method) — used to validate worker existence.
    - self.capp (attribute) — used to call the .control.broadcast method.
    - self.error_reason (method) — used to compute a failure reason string.
    - self.write (method) — used to write response body content.
    - self.set_status (method) — used to set HTTP status code.
    - module-level logger (logger) — used to log info and error messages.

Attributes WRITTEN:
    - No instance attributes (self.<attr>) are assigned or mutated by this method.
    - The outgoing HTTP response state is mutated:
        - On success: writes a dict message to response body (implicitly the HTTP status remains 200 unless changed elsewhere).
        - On failure: sets status to 403 and writes a plain-text failure message.

## Constraints:
Preconditions:
    - Caller must be authenticated (enforced by web.authenticated).
    - self.is_worker(workername) must return True; otherwise a 404 HTTPError is raised and no broadcast is attempted.
    - self.capp and self.capp.control.broadcast must be available and accept the called parameters.

Postconditions:
    - If the broadcast reply satisfies the success condition, the HTTP response body contains a success dict and no explicit error status is set by this method.
    - If the broadcast reply does not satisfy the success condition, the handler logs the raw reply, sets status 403, and writes a failure message that includes the reason returned by self.error_reason(workername, response).
    - If the broadcast reply has an unexpected structure, an unhandled KeyError/IndexError/TypeError may propagate out of the handler.

## Side Effects:
    - Network / IPC: invokes self.capp.control.broadcast(...) which performs an external control action (likely involving network or inter-process communication).
    - Logging: logs an info-level message when attempting the restart and an error-level message containing the raw response on failure.
    - HTTP response mutation: writes either a dict (success) or a plain string (failure) to the response body and may set the HTTP status to 403.

## `flower.api.control.WorkerPoolGrow` · *class*

## Summary:
WorkerPoolGrow is a Tornado HTTP request handler class (subclassing ControlHandler) whose POST endpoint requests an increase of a named worker's concurrency pool by invoking the application's control API and writing a success or failure HTTP response.

## Description:
This handler is executed per-request by Tornado when an authenticated POST arrives at the route bound to WorkerPoolGrow. The post method:
- Validates the worker exists using ControlHandler.is_worker.
- Parses an integer request parameter 'n' (default 1).
- Calls self.capp.control.pool_grow(n=n, reply=True, destination=[workername]) to request pool growth on the target worker.
- Interprets the returned broadcast response using the exact conditional present in the code and writes the HTTP response accordingly.

Responsibility:
- HTTP-layer responsibilities only: input parsing, worker identity validation, invoking the control RPC, interpreting its immediate response for success/failure, logging, and writing the HTTP response. It delegates worker membership checks and error-extraction to ControlHandler and the actual pool mutation to self.capp.control.

Known instantiation:
- Created by Tornado's request dispatcher (no custom __init__). The post method is decorated with @web.authenticated and thus runs only for authenticated requests (per Tornado/web.authenticated semantics).

## Signature:
- def post(self, workername)
  - workername (str): the worker identifier passed as a path parameter by Tornado routing.

## State:
This class adds no instance attributes. It depends on inherited/application/module-level objects:

- self.application
  - Must exist and expose a workers collection used by ControlHandler.is_worker for membership testing.

- self.capp
  - Must exist and expose .control.pool_grow callable.
  - Required call used by the code:
      pool_grow(n: int, reply: bool, destination: list[str]) -> response

- Expected minimal response shape (as required by the code):
  - response is an iterable (commonly a list or tuple).
  - The code reads response[0][workername] and then tests 'ok' in that mapping.
  - Minimal example the handler expects to succeed:
      response == [{ workername: {'ok': <any> , ... }, ... }, ...]
  - If response is falsy (None, empty sequence, empty container), the success condition is considered false.

- Module-level logger (logging.Logger) named logger:
  - Used with the exact format strings from the code:
      logger.info("Growing '%s' worker's pool by '%s'", workername, n)
      logger.error(response)

- RequestHandler helpers used:
  - self.get_argument(name, default, type=...) — used to parse 'n'.
  - self.write(body) — called with a dict on success and a plain string on failure.
  - self.set_status(code) — used to set 403 on failure.

Class invariants:
- Instances must have valid self.application and self.capp attributes for the handler to work.
- post assumes it runs under an authenticated request due to @web.authenticated.

## Lifecycle:
Creation:
- No custom constructor; instantiate via Tornado routing.

Usage sequence (per-request):
1. Tornado calls post(self, workername) on an authenticated request.
2. Worker validation:
   - if not self.is_worker(workername):
       raise web.HTTPError(404, f"Unknown worker '{workername}'")
3. Read 'n':
   - n = self.get_argument('n', default=1, type=int)
4. Log attempt:
   - logger.info("Growing '%s' worker's pool by '%s'", workername, n)
5. Call control RPC:
   - response = self.capp.control.pool_grow(n=n, reply=True, destination=[workername])
6. Inspect and respond using the exact conditional:
   - if response and 'ok' in response[0][workername]:
       self.write(dict(message=f"Growing '{workername}' worker's pool by {n}"))
     else:
       logger.error(response)
       self.set_status(403)
       reason = self.error_reason(workername, response)
       self.write(f"Failed to grow '{workername}' worker's pool: {reason}")
7. Tornado finalizes response and discards the handler.

Destruction:
- No cleanup; Tornado disposes of the handler after the request.

## Side effects:
- Logs informational message on attempt using the precise format shown above.
- Calls into the application control plane (self.capp.control.pool_grow) which may trigger remote-side changes.
- Writes to the HTTP response body via self.write(...) and may change HTTP status via self.set_status(403) on failure.

## Exact conditional for success (literal from source):
- The code treats the call as successful if and only if:
    response and 'ok' in response[0][workername]
  This is evaluated in the order shown (truthiness of response first, then membership of 'ok' in the mapping at response[0][workername]).

## Raises:
- Explicit raise in code:
  - web.HTTPError(404, f"Unknown worker '{workername}'")
    - Raised when ControlHandler.is_worker(workername) returns a falsy value.

- Exceptions that can propagate from specific lines in the implementation:
  - self.get_argument may raise (argument missing or type conversion error) depending on Tornado's RequestHandler.get_argument behavior.
  - AttributeError:
      - If self.capp or self.capp.control is missing when calling pool_grow.
      - If self.error_reason is missing (unlikely since inherited from ControlHandler).
  - IndexError:
      - If response is truthy but an attempt to access response[0] is invalid for that object (rare if response is a non-empty iterable).
  - KeyError:
      - If response[0] does not contain workername, then response[0][workername] raises KeyError when evaluated; this will propagate since the code does not catch it.
  - TypeError or AttributeError during "'ok' in response[0][workername]":
      - If response[0][workername] is not a mapping-like object supporting membership tests, the 'in' expression may raise.
  - Any exception raised by self.capp.control.pool_grow itself (network, RPC, or domain-specific exceptions).

Note: The code intentionally does not catch these general exceptions; they will propagate to Tornado's global handler unless wrapped elsewhere.

## Edge cases:
- Falsy response (None or empty sequence):
  - The truthiness check (if response and ...) prevents immediate indexing of response[0] when response is falsy; in that case the handler follows the failure path.
- response truthy but missing worker key:
  - If response is truthy but response[0] lacks workername, attempting response[0][workername] raises KeyError which is not handled here.
- Non-mapping worker value:
  - If response[0][workername] exists but is not mapping-like, "'ok' in response[0][workername]" may raise TypeError or AttributeError.
- 'n' value validation:
  - The handler does not validate that n > 0. Negative or zero values are forwarded to pool_grow unchanged.

## Returns:
- The post method does not return a Python value (returns None). It produces an HTTP response:
  - Success path: calls self.write(dict(message=...)); HTTP status remains Tornado's default (typically 200).
  - Failure path: sets HTTP status to 403 and writes a plain string failure message.

## Example (textual flow):
- Client: Authenticated POST to route bound to WorkerPoolGrow with path parameter workername and query/body parameter n=2.
- Handler actions:
  - Validates worker via is_worker.
  - Parses n (2).
  - Calls pool_grow(n=2, reply=True, destination=[workername]).
  - If pool_grow returns [{workername: {'ok': True}}], writes {"message": "Growing '<workername>' worker's pool by 2"} and responds 200.
  - Otherwise logs the response, sets status 403, computes reason via error_reason, and writes "Failed to grow '<workername>' worker's pool: <reason>".

Implementation reproduction checklist:
- Subclass ControlHandler.
- Implement post(self, workername) exactly as described in the Usage sequence.
- Protect the route with web.authenticated (the post method in the real code is decorated with @web.authenticated).
- Ensure the application object provided by Tornado exposes a workers collection and that self.capp.control.pool_grow exists and returns a response shape compatible with the success conditional above.

### `flower.api.control.WorkerPoolGrow.post` · *method*

## Summary:
Handle an HTTP POST that requests growing a specific worker's concurrency pool and produce an HTTP response indicating success or failure; it affects external state by invoking the application's control API (pool_grow) and by writing to the HTTP response.

## Description:
This method is a Tornado HTTP POST handler invoked when a client requests that a worker increase its concurrency pool. It runs during request handling (the authenticated API request lifecycle) and performs the following main steps:
- Validate that the named worker exists.
- Read the optional 'n' POST/GET argument (number of worker processes/threads to add), defaulting to 1.
- Call the application's control API (self.capp.control.pool_grow) to request the pool growth on the remote worker.
- Write a success message to the HTTP response when the control API reports success, otherwise log the failure, set HTTP 403, and write a failure message with a reason.

Known callers / invocation context:
- Tornado's request dispatch: this is the method executed for an authenticated HTTP POST to the route handled by WorkerPoolGrow (decorated with @web.authenticated). It is not intended to be called from within business logic directly; it is an HTTP endpoint handler.

Why this logic is separated:
- It composes several distinct concerns (input parsing, worker existence validation, remote control RPC, response formatting and error handling) that belong to the HTTP handler layer. Keeping it as its own method keeps request/response handling encapsulated and allows reuse of ControlHandler helpers (is_worker, error_reason, write, set_status).

## Args:
    workername (str):
        - The identifier/name of the target worker whose pool should be grown.
        - Expected to be a non-empty string that corresponds to a known worker in the system.

    HTTP request argument 'n' (via self.get_argument):
        - Type: int
        - Name in request: 'n'
        - Allowed values: any integer accepted by the underlying system; negative or zero values are not specially handled in this method (validation if required must be enforced elsewhere).
        - Default: 1
        - Notes: the value is obtained using self.get_argument('n', default=1, type=int), so conversion to int is performed by the underlying RequestHandler implementation and may raise an error if conversion fails.

## Returns:
    None
    - The method does not return a Python value; it writes to the HTTP response (self.write) and may set the HTTP status (self.set_status).
    - Success path: writes a JSON-like dict with message "Growing '<workername>' worker's pool by <n>" and leaves the response status at Tornado's default (200) unless another handler sets it.
    - Failure path: sets HTTP status to 403 and writes a plain-text failure string "Failed to grow '<workername>' worker's pool: <reason>".

## Raises:
    tornado.web.HTTPError(404):
        - Triggered when self.is_worker(workername) returns a falsy value. The exact raised error is:
          web.HTTPError(404, f"Unknown worker '{workername}'")

    Other exceptions (not explicitly caught here):
        - Exceptions raised by underlying calls may propagate:
            * Exceptions from self.get_argument if argument conversion fails (behavior depends on RequestHandler implementation).
            * Exceptions raised by self.capp.control.pool_grow (network/RPC or internal errors).
            * IndexError/KeyError if the response returned by pool_grow does not match the expected structure (the code indexes response[0] and then response[0][workername]).
        - These are not caught inside this method and will propagate to Tornado's exception handling.

## State Changes:
Attributes READ:
    - self.capp
        * Used to call self.capp.control.pool_grow(...)
    - (indirect) self.is_worker, self.get_argument, self.error_reason
        * These instance methods are invoked; they read whatever internal state they use (not enumerated here).

Attributes WRITTEN:
    - None of the object's stored attributes are assigned to or mutated directly by this method (no self.<attr> assignments). However, the method mutates the HTTP response state via:
        * self.write(...) - appends content to the HTTP response body
        * self.set_status(...) - may change the HTTP response status code

## Constraints:
Preconditions:
    - The caller must be authenticated (method is decorated with @web.authenticated).
    - self must expose:
        * is_worker(workername) -> truthy/falsy to validate worker existence
        * get_argument(name, default, type) to parse request params
        * error_reason(workername, response) to compute a human-readable failure reason
        * capp with a .control.pool_grow(...) callable that accepts (n=int, reply=True, destination=[workername]) and returns a response structure the method expects
    - workername should correspond to an existing worker (otherwise a 404 HTTPError is raised).

Postconditions:
    - On success (when response is truthy and response[0][workername] contains 'ok'):
        * An HTTP response body is written with a success message.
        * The HTTP status remains the default (200) unless modified elsewhere.
    - On failure (including when response is falsy or the expected 'ok' flag is absent):
        * The method logs the raw response at ERROR level.
        * The HTTP response status is set to 403 and a failure message including a reason (from self.error_reason) is written.
    - If the worker is unknown, a web.HTTPError(404, ...) is raised and no further actions occur in this method.

## Side Effects:
    - Emits logging:
        * logger.info(...) on attempt to grow the pool.
        * logger.error(...) when the control API response indicates failure or unexpected shape.
    - Sends a control command to the application/worker management system:
        * Calls self.capp.control.pool_grow(n=n, reply=True, destination=[workername]) — this is typically an RPC or control-plane call that causes actual worker pool changes.
    - Mutates the HTTP response:
        * Writes response body content via self.write(...)
        * May set HTTP status via self.set_status(403)
    - May allow exceptions from lower layers to propagate (no general try/except is present), which will be handled by Tornado's global exception handling.

## Edge cases & notes:
    - If pool_grow returns an unexpected structure (e.g., response is a list but response[0] doesn't contain the workername key), the check 'ok' in response[0][workername] can raise a KeyError or other exception; such exceptions are not handled here.
    - The method does not perform deep validation of 'n' (e.g., non-negative); invalid values may be accepted and forwarded to the control API.
    - The human-readable failure reason depends on the implementation of self.error_reason; this method only delegates to it when the control API indicates failure.

## `flower.api.control.WorkerPoolShrink` · *class*

## Summary:
Handles authenticated HTTP POST requests to shrink a specific worker's pool by N worker processes; validates the worker name, reads the shrink amount, invokes the application control API, and returns a success message or a failure reason.

## Description:
This Tornado request handler implements the control endpoint that reduces (shrinks) the concurrency pool for a single worker. It is intended to be used as a per-request handler class in the Flower web application routing table for a route that includes a worker identifier (workername) in the URL path.

Typical usage scenario:
- A client (typically the Flower web UI or an API consumer) issues an authenticated POST to the route bound to this handler, passing the worker name in the URL and optionally an "n" argument (number of pool slots to remove).
- The handler verifies the worker exists, reads the integer argument n (default 1), calls the application control interface to request a pool shrink on that worker, and returns a JSON success message if the operation reports success for that worker. On failure it logs the response, sets HTTP status 403, and writes a human-readable failure message extracted via the ControlHandler.error_reason helper.

Known callers/factories:
- Tornado's routing and request instantiation — the handler is constructed by Tornado for each matching HTTP request.
- The Flower web UI or any authenticated HTTP client that posts to the control route for shrinking a worker's pool.

Motivation and responsibilities:
- Encapsulates the HTTP-layer logic (authentication enforcement, argument parsing, response formatting and status codes) for a single control action: shrinking a worker's pool.
- Delegates worker membership checks and error-reason extraction to ControlHandler to avoid duplicating those utilities.
- Delegates the actual control action to the application's control API (self.capp.control.pool_shrink).

## State:
This class defines no instance attributes of its own. It depends on inherited/request-provided attributes and module-level variables:

- self (inherited Tornado RequestHandler instance)
  - Required/requested attributes/methods (assumed to exist at runtime):
    - is_worker(workername) -> truthy/falsy (inherited from ControlHandler): membership check for workername.
    - error_reason(workername, response) (inherited from ControlHandler): extracts a human-readable error message from a control response aggregation.
    - get_argument(name, default, type=int) (Tornado RequestHandler): reads an HTTP argument and optionally converts it to a type.
    - write(obj_or_str) (Tornado RequestHandler): writes a response body; when passed a dict, Tornado serializes to JSON.
    - set_status(code) (Tornado RequestHandler): sets the HTTP response status code.
    - self.capp: application object with a .control attribute exposing control operations. This class uses self.capp.control.pool_shrink(...) — the implementation must provide that attribute and method.
- logger (module-level logging.Logger)
  - Used for informational and error logging (logger.info, logger.error).

Attribute types and constraints:
- workername (URL path component provided to post): expected to be a str (hashable, non-empty) representing a worker identifier.
- n (argument extracted via get_argument): int, default 1. No further validation performed (e.g., non-negativity) by this handler.

Class invariants:
- The handler assumes self.capp and self.application (and their expected internals) are present and valid when post() is invoked.
- The ControlHandler helpers is_worker and error_reason behave as documented (membership test and response parsing respectively).

## Lifecycle:
Creation:
- Instantiated by Tornado per request; no custom __init__ parameters.
- No additional factory methods are required.

Usage (typical call sequence):
1. Tornado instantiates WorkerPoolShrink for an incoming POST.
2. Tornado invokes post(self, workername) with workername extracted from the route.
3. The handler:
   a. Verifies worker existence via self.is_worker(workername).
   b. Reads integer argument 'n' from the request (default 1).
   c. Calls self.capp.control.pool_shrink(n=n, reply=True, destination=[workername]).
   d. If the returned response indicates success for the given worker, writes a JSON message describing the shrink and returns HTTP 200.
   e. Otherwise, logs the response, sets HTTP status 403, obtains a failure reason via self.error_reason(workername, response), and writes a failure message.

Destruction / cleanup:
- No cleanup or context-manager behavior required. Tornado discards the handler at the end of the request.

Sequencing rules and requirements:
- Authentication: the method is decorated with @web.authenticated, therefore the runtime environment must ensure the decorator is effective (i.e., authentication middleware provided by Tornado/BaseApiHandler).
- is_worker must be called before attempting pool_shrink to avoid issuing control operations for unknown workers.
- No explicit ordering constraints beyond the sequence described; methods are synchronous in this handler's flow.

## Method Map:
graph LR
    HTTP_POST[POST /.../<workername>] --> AUTH[web.authenticated decorator]
    AUTH --> POST_METHOD[post(workername)]
    POST_METHOD --> IS_WORKER[is_worker(workername)]
    IS_WORKER -->|not found| HTTP_404[raise web.HTTPError(404)]
    POST_METHOD --> GET_ARG[get_argument('n', default=1, type=int)]
    GET_ARG --> LOG_INFO[logger.info(...)]
    LOG_INFO --> POOL_SHRINK[self.capp.control.pool_shrink(n=n, reply=True, destination=[workername])]
    POOL_SHRINK -->|response indicates ok| WRITE_SUCCESS[write(dict(message=...)) -> HTTP 200]
    POOL_SHRINK -->|failure or unexpected| LOG_ERROR[logger.error(response)]
    LOG_ERROR --> SET_STATUS[set_status(403)]
    SET_STATUS --> REASON[error_reason(workername, response)]
    REASON --> WRITE_FAILURE[write(f"Failed to shrink ...: {reason}")]

## Raises:
Exceptions explicitly and implicitly raised by post:
- web.HTTPError(404, f"Unknown worker '{workername}'")
  - Raised when self.is_worker(workername) is falsy (worker not known). This is the handler's explicit error response for unknown workers.
- Type/Value errors from get_argument:
  - If the client supplies an 'n' value that cannot be converted to int, the underlying conversion may raise ValueError or TypeError which will propagate (no local handling). When no 'n' is supplied, the default 1 is used (no error).
- Exceptions from self.capp.control.pool_shrink:
  - pool_shrink may raise arbitrary exceptions (network, RPC, attribute errors) depending on the application's control API implementation; these exceptions are not caught here and will propagate.
- IndexError/KeyError/TypeError:
  - The handler examines response and then accesses response[0][workername]; if response is falsy the condition prevents the success branch, but if response exists with unexpected shape (e.g., not indexable, missing keys), those indexing/subscript operations may raise IndexError/KeyError/TypeError and propagate.
- AttributeError:
  - If required inherited attributes (self.capp, self.get_argument, self.is_worker, self.write, self.set_status, self.error_reason) or module-level logger are missing, AttributeError will be raised when accessed.

Note: The handler returns 403 for operations that return a response that does not include 'ok' for the targeted worker (it does not convert unexpected responses into 404; it logs and responds 403).

## Example:
- HTTP semantics (conceptual):
  1. Client issues POST to /control/workers/<workername>/pool/shrink with form/query parameter n=2 (authentication provided).
  2. Handler post executes:
     - is_worker('<workername>') -> True
     - get_argument('n', default=1, type=int) -> 2
     - self.capp.control.pool_shrink(n=2, reply=True, destination=['<workername>']) -> response
     - If response is like [{'<workername>': {'ok': True}}], handler writes:
         {"message": "Shrinking '<workername>' worker's pool by 2"} with HTTP 200.
     - If response indicates failure (no 'ok' key for that worker), handler logs the response, sets HTTP status 403, determines reason = self.error_reason('<workername>', response), and writes:
         "Failed to shrink '<workername>' worker's pool: {reason}"

Implementation notes for re-implementation:
- Ensure the runtime provides:
  - Tornado RequestHandler semantics (get_argument, write, set_status).
  - Authentication decorator web.authenticated is applied to enforce authentication.
  - A ControlHandler-like mixin providing is_worker and error_reason helpers.
  - An application object accessible at runtime exposing self.capp with a control.pool_shrink method that accepts the same keyword arguments (n, reply, destination) and returns a list/iterable of mappings where response[0][workername] is a mapping possibly containing an 'ok' key on success.
- Do not add additional validations (e.g., n >= 1) unless desired; the original handler only ensures n is coerced to int and uses the provided value.

### `flower.api.control.WorkerPoolShrink.post` · *method*

## Summary:
Handles an authenticated HTTP POST request to shrink a worker's process pool by calling the Celery control API and writing an appropriate HTTP response; it changes no persistent attributes on the handler itself.

## Description:
This method is an HTTP POST handler executed when a client (typically the Flower web UI or an HTTP API client) requests that a specific worker reduce its pool size. It runs during request handling in Tornado's request lifecycle and requires an authenticated session (@web.authenticated on the enclosing class).

It is implemented as a separate method because it encapsulates the full request handling flow for this specific API endpoint: validate the target worker, parse the request parameter, perform the control RPC call (capp.control.pool_shrink), and produce HTTP responses for both success and failure. Keeping it separate keeps routing/authorization, argument parsing, control API invocation, and response generation localized and testable.

Known callers / invocation context:
- Tornado's routing dispatch invokes this method when a POST request is routed to the WorkerPoolShrink handler for a given workername.
- Typical callers are the Flower web UI and clients of Flower's HTTP API initiating a pool-shrink operation.

## Args:
    workername (str): The worker identifier taken from the request URL or route. Must reference a known worker according to self.is_worker.

Request argument (HTTP parameter):
    n (int): Optional request parameter parsed via self.get_argument('n', default=1, type=int). Represents the number of processes to remove from the worker's pool. If omitted, defaults to 1. The method does not perform further validation on numeric range.

## Returns:
    None: The method does not return a Python value. Instead it sends an HTTP response:
        - Success: writes a JSON object {"message": "Shrinking '<workername>' worker's pool by <n>"} and leaves the default 200 response status.
        - Failure: sets HTTP status 403 and writes a plain text message explaining the failure.

## Raises:
    tornado.web.HTTPError(404): Raised immediately if self.is_worker(workername) evaluates to False. The error message is exactly: "Unknown worker '<workername>'".
    (No other exceptions are explicitly raised by this method in the source; errors from underlying calls such as self.get_argument or capp.control.pool_shrink may propagate depending on their implementations.)

## State Changes:
Attributes READ:
    self.is_worker (call) - used to validate that the supplied workername identifies a known worker
    self.get_argument (call) - used to read the 'n' argument from the HTTP request
    self.capp (attribute) - accessed to call self.capp.control.pool_shrink(...)
    self.capp.control.pool_shrink (call) - invoked to request the worker to shrink its pool
    self.error_reason (call) - used to compute a human-readable reason string if the control call fails
    self.write (call) - used to write the HTTP response body
    self.set_status (call) - used to set HTTP response status to 403 on failure
    Module-level logger (logger.info / logger.error) - used for informational and error logging

Attributes WRITTEN:
    None — the method does not modify persistent attributes on self; it only writes to the HTTP response and performs external calls.

## Constraints:
Preconditions:
    - The request must be authenticated (enforced by @web.authenticated on the handler class).
    - The supplied workername must satisfy self.is_worker(workername); otherwise a 404 is raised.
    - The 'n' parameter is expected to be convertible to int by self.get_argument(..., type=int). The method assumes get_argument returns an int when provided.

Postconditions:
    - On success (response from capp.control.pool_shrink contains an 'ok' entry for this worker as checked by if response and 'ok' in response[0][workername]): the HTTP response body will contain a JSON message noting the shrink and the HTTP status will remain the default (200).
    - On failure (no response or missing 'ok' for this worker): the handler logs the raw response, sets HTTP status to 403, and writes a failure message that includes the result of self.error_reason(workername, response).

## Side Effects:
    - Makes an external control RPC call: self.capp.control.pool_shrink(n=n, reply=True, destination=[workername]) which triggers actions in the Celery worker/control subsystem.
    - Writes to the HTTP response stream via self.write and may change HTTP status via self.set_status.
    - Emits log messages via logger.info on the attempted shrink and logger.error on failure.
    - Does not perform direct persistent mutation of the handler's attributes.

## `flower.api.control.WorkerPoolAutoscale` · *class*

## Summary:
HTTP request handler that exposes a POST endpoint to trigger autoscaling for a single worker. It validates the worker, parses numeric min/max arguments from the request, dispatches an autoscale control command to the application control interface, and writes an appropriate HTTP response indicating success or failure.

## Description:
WorkerPoolAutoscale is a lightweight Tornado request handler class (subclassing ControlHandler) intended to be registered as the handler for a per-worker autoscale POST route in the Flower web API. Typical instantiation is performed by Tornado when a route is bound to this handler class (per-request handler objects are created for each incoming HTTP request). The handler's responsibility is strictly HTTP-facing: validate path parameters, parse request arguments, call into the application control API to request autoscaling on a specific worker, and translate the control API's aggregated response into a concise HTTP response for the client.

This class separates HTTP concerns (authentication, request parsing, status codes, response body serialization) from lower-level autoscale logic (which is performed by the application's control broadcast mechanism). It relies on ControlHandler for small helper utilities (is_worker and error_reason) and on the application instance available on the handler (self.capp) to perform the control broadcast.

Known callers / creation sites:
- Tornado's routing machinery when the autoscale endpoint is requested by a client (e.g., POST /api/workers/<workername>/autoscale).
- Any unit tests or integration tests that instantiate request handlers to exercise the HTTP interface.

Motivation and responsibility boundary:
- Motivation: centralize the HTTP-side flow for autoscaling a single worker so UI and API clients have a consistent endpoint and behavior.
- Boundary: does not implement autoscaling logic itself; it only forwards the autoscale request to self.capp.control.broadcast and interprets the returned aggregation.

## State:
This class defines no persistent instance attributes of its own. It depends on state inherited from Tornado/BaseApiHandler and utilities provided by the ControlHandler mixin.

Attributes relied upon (inherited / external):
- self.application (Tornado application object)
  - Expected to expose application.workers, a container supporting membership testing (workername in application.workers).
- self.capp
  - Expected to expose capp.control.broadcast(...) which accepts the signature shown below and returns an aggregation response (iterable of mappings).
- Methods inherited from RequestHandler / BaseApiHandler / ControlHandler:
  - self.get_argument(name, type=...): reads HTTP request arguments.
  - self.write(body): writes content to the HTTP response body.
  - self.set_status(code): sets the HTTP response status code.
  - self.is_worker(workername): helper from ControlHandler to validate worker membership.
  - self.error_reason(workername, response): helper from ControlHandler to extract a human-readable error for a given worker from a broadcast response.

Module-level variables referenced:
- logger (module-level logging.Logger): used for info and error logging.

Valid values / invariants:
- The handler assumes that self.capp.control.broadcast returns a response that is an iterable (commonly a list) of mapping-like entries, where each entry maps workername -> result-dict for that invocation.
- For success detection this implementation expects response[0][workername] to exist and to contain an 'ok' key indicating success. If the shape deviates, the handler treats the result as a failure path.

Class invariants:
- No instance attributes are introduced by this class; it does not mutate application-level state.
- The handler must be used in a request context where inherited methods and attributes (get_argument, write, set_status, is_worker, error_reason, capp) are available.

## Lifecycle:
Creation:
- Instantiated by Tornado when a route maps to this handler class (no custom constructor arguments). No explicit initialization is required by callers.

Usage (typical call sequence per request):
1. Tornado calls the decorated method post(self, workername) when an authenticated POST request for the autoscale route is received (the decorator @web.authenticated enforces authentication before method execution).
2. The method checks worker membership via self.is_worker(workername).
   - If the worker is unknown, the method raises tornado.web.HTTPError(404) immediately; no further processing occurs.
3. The method reads the integer arguments 'min' and 'max' from the HTTP request via self.get_argument('min', type=int) and self.get_argument('max', type=int). These calls will raise if the parameters are missing or cannot be converted to int, and such exceptions propagate (typically resulting in a 400/500 by Tornado or upstream layers).
4. The method logs an info message indicating the autoscale request.
5. It calls self.capp.control.broadcast('autoscale', arguments={'min': min, 'max': max}, destination=[workername], reply=True) to send the control command and capture the aggregated response.
6. The response is inspected:
   - Success branch: if response is truthy and response[0][workername] contains an 'ok' key, the handler writes a JSON-like dict message describing the autoscale request (e.g., {"message": "Autoscaling 'X' worker (min=..., max=...)"}) and leaves the status as the default (typically 200).
   - Failure branch: otherwise, the raw response is logged at error level, self.set_status(403) is called, a textual failure message is written that includes the reason derived from self.error_reason(workername, response).
7. Tornado completes the request and disposes of the handler instance.

Destruction / cleanup:
- No cleanup required. Tornado disposes of the per-request handler instance after the request finishes.

Sequencing constraints:
- post must be called in a valid Tornado request context where authentication and request parsing are available and where self.capp is set on the application or handler. Authentication is enforced by the @web.authenticated decorator and will prevent entry into post on unauthenticated requests.

## Method Map:
graph TD
    POST[post(workername) - HTTP POST entry point]
    POST --> AUTH[web.authenticated (decorator)]
    POST --> ISW[self.is_worker(workername)]
    POST --> GA_MIN[self.get_argument('min', type=int)]
    POST --> GA_MAX[self.get_argument('max', type=int)]
    POST --> LOGI[logger.info(...)]
    POST --> BROAD[self.capp.control.broadcast('autoscale', arguments={'min','max'}, destination=[worker]) ]
    BROAD --> CHECK[inspect response]
    CHECK --> SUCCESS[write success dict]
    CHECK --> FAILURE[logger.error(response) -> set_status(403) -> reason = self.error_reason(...) -> write failure message]

(Note: diagram shows typical invocation order and dependencies; self.write and self.set_status are called from success/failure branches.)

## Behavior details (post):
Inputs:
- workername (str): path parameter extracted by Tornado from the route. Expected to identify a worker known to the application.
- HTTP request arguments (form/query/body as provided to Tornado):
  - 'min' (required): convertible to int via self.get_argument(name, type=int).
  - 'max' (required): convertible to int via self.get_argument(name, type=int).

Outputs / side effects:
- Writes to the HTTP response via self.write(...):
  - On success: writes a mapping/dict-like object containing a human-readable success message.
  - On failure: writes a plain-text failure message including the reason.
- May set HTTP response status to 403 on failure.
- Logs an info-level entry when attempting autoscale and an error-level entry if the broadcast response is not recognized as successful.
- Calls an external control RPC: self.capp.control.broadcast(...), which may perform I/O and mutate external system state (actual autoscaling operation).

Success criterion:
- The method treats the call as successful if and only if:
  - the returned response is truthy, and
  - response[0][workername] exists and contains an 'ok' key.
  This check is intentionally strict and tied to the expected format of the control broadcast result aggregation.

Edge cases and failure modes:
- Unknown worker:
  - self.is_worker(workername) falsy -> tornado.web.HTTPError(404) is raised immediately.
- Missing or non-integer 'min'/'max' arguments:
  - self.get_argument will raise (TypeError/ValueError or tornado-specific exception) and such exceptions propagate; they are not handled by this method.
- Unexpected broadcast response shape:
  - If response is falsy, empty, or does not contain response[0][workername]['ok'], the method enters the failure branch: logs the raw response, sets status 403, derives a reason via self.error_reason and writes failure text.
  - If response contains entries but response[0][workername] is missing or maps to a non-mapping object, KeyError / AttributeError may be raised when indexing or accessing keys; these exceptions are not caught here and will propagate (but typical broadcast responses follow the expected shape).
- Any exceptions raised by self.capp.control.broadcast will propagate unless upper layers catch them.

## Raises:
- tornado.web.HTTPError(404): if the provided workername is not recognized (self.is_worker returns falsy).
- Exceptions from self.get_argument for missing/invalid 'min'/'max' (propagated from Tornado's argument parsing).
- Exceptions from self.capp.control.broadcast or from malformed response inspection (e.g., KeyError, TypeError, AttributeError) may propagate if the broadcast return shape is unexpected.

Note: WorkerPoolAutoscale does not define its own __init__; therefore standard Tornado / BaseApiHandler initialization semantics and exceptions apply at construction time.

## Example (usage narrative):
1. A client issues POST /api/workers/worker@example.com/autoscale with form/query parameters min=2 and max=10.
2. Tornado authenticates the request (web.authenticated). Tornado instantiates WorkerPoolAutoscale for the request and calls post(self, 'worker@example.com').
3. post validates the worker exists using self.is_worker('worker@example.com').
4. post reads min and max as integers via self.get_argument.
5. post logs the autoscale attempt and calls self.capp.control.broadcast('autoscale', arguments={'min': 2, 'max': 10}, destination=['worker@example.com'], reply=True).
6. If the control broadcast response indicates success for that worker (response[0]['worker@example.com'] contains an 'ok' key), post writes a JSON-like success message and the request finishes with status 200.
7. If the response does not indicate success, post logs the response, sets response status to 403, extracts a human-readable reason via self.error_reason and writes a failure message containing that reason.

This documentation contains the inputs, outputs, side effects, invariants, and expected control flow necessary to reimplement the WorkerPoolAutoscale class's behavior in another codebase or for writing tests that exercise its common success and failure paths.

### `flower.api.control.WorkerPoolAutoscale.post` · *method*

## Summary:
Handles an HTTP POST request to trigger autoscaling of a specific worker; validates the worker exists, reads the requested min/max worker counts from the request, issues an autoscale control command, and writes a success or failure HTTP response (potentially changing the response status).

## Description:
This method is the HTTP POST handler for initiating autoscale operations on a single worker. Typical callers:
- The Tornado web server's request dispatch when a client issues the API POST to the autoscale endpoint for a worker (i.e., it runs in the request lifecycle as the handler for the POST route bound to this handler class).
This method is separated from other logic because it performs the HTTP-specific task of:
- validating the path parameter (worker name),
- extracting HTTP request arguments,
- invoking the application control API to perform autoscaling,
- and serializing an appropriate HTTP response. Keeping this behavior in a distinct handler method keeps HTTP concerns (request parsing, response writing, status codes) separate from lower-level control logic.

## Args:
    workername (str): The worker identifier extracted from the request path. Must correspond to a known worker; otherwise a 404 HTTPError is raised.

## Returns:
    None
    - The method writes the HTTP response body via self.write(...) and may change the response status via self.set_status(...). It does not return a Python value.

## Raises:
    tornado.web.HTTPError(404):
        - Raised when the provided workername is not recognized (i.e., self.is_worker(workername) returns False).
    (Other exceptions from underlying calls may propagate; the method does not catch them.)

## State Changes:
Attributes READ:
    - self.is_worker: checked to validate workername exists.
    - self.get_argument: called twice to read 'min' and 'max' from the HTTP request (with type=int).
    - self.capp and self.capp.control: used to call broadcast(...) to request autoscaling.
    - self.error_reason: used to compute a textual reason when autoscale fails.
    - logger (module-level): used to log info/error messages (logger.info, logger.error).

Attributes WRITTEN:
    - None of the handler's self.<attr> fields are modified by this method. Instead, the method mutates the HTTP response via the handler API (see Side Effects).

## Constraints:
Preconditions:
    - The handler instance must implement the helper methods used here:
        * is_worker(workername) -> bool
        * get_argument(name, type=...) -> converted value
        * error_reason(workername, response) -> str
        * write(content) and set_status(code)
      These are expected to be available on the handler class.
    - The HTTP request must include query/form arguments 'min' and 'max' that can be parsed with type=int by self.get_argument; otherwise argument-parsing failures from the request framework will propagate.
    - workername must be a valid/known worker (self.is_worker must return True) to avoid the 404 branch.

Postconditions:
    - On success (broadcast response indicates success for the worker), a JSON-like dict message is written to the response body describing the autoscale request; response status remains the default (typically 200).
    - On failure (broadcast did not return the expected success marker), the response status is set to 403 and a plain-text failure message is written; the broadcast response is logged at error level.
    - If preconditions fail (unknown worker), a 404 HTTPError is raised and no further actions in this method are executed.

## Side Effects:
    - Logs an informational message via logger.info when attempting autoscaling and logs the raw broadcast response via logger.error if autoscale fails.
    - Calls an external control API: self.capp.control.broadcast('autoscale', arguments={'min': min, 'max': max}, destination=[workername], reply=True). This is an outbound RPC/control operation that may perform network I/O or cause external state changes (actual autoscaling).
    - Writes to the HTTP response body via self.write(...) and may set the response status via self.set_status(...), affecting the outgoing HTTP reply sent to the client.
    - May allow exceptions from lower-level operations (argument parsing, broadcast) to propagate up the request handling stack.

## `flower.api.control.WorkerQueueAddConsumer` · *class*

## Summary:
A Tornado HTTP handler that processes POST requests to add a queue consumer on a specific worker by issuing a control broadcast and returning the worker's response.

## Description:
This handler should be instantiated by Tornado's routing when exposing an HTTP API endpoint that allows an authenticated user to ask a worker to start consuming a given queue. The method implemented is a single POST endpoint (decorated with tornado.web.authenticated), so the caller must be an authenticated HTTP client.

Typical usage scenarios:
- An HTTP API route routes POST requests for adding consumers to WorkerQueueAddConsumer.
- A UI or API client posts a form or JSON with a 'queue' parameter to instruct a specific worker to add a consumer for that queue.

Responsibility boundary:
- Validate that the named worker exists (via is_worker).
- Extract the 'queue' argument from the request.
- Send a control command ('add_consumer') to the specific worker via self.capp.control.broadcast.
- Translate the worker's reply into an HTTP response: on success write a JSON success message; on failure log, set 403, and write a human-readable failure reason.
It does not itself perform any consumer startup logic — it forwards the request to the worker control layer and surfaces the response.

## State:
This class has no custom __init__ and relies on its ControlHandler superclass for shared state. The component references the following runtime attributes (inherited or module-level) which must exist and satisfy the invariants below:

- self.capp
  - Type: application/context object (exact type provided by the surrounding system)
  - Required interface: has attribute control with method broadcast(command_name, arguments, destination, reply)
  - Invariant: self.capp.control.broadcast(...) is callable and returns a reply structure the handler can inspect.

- self.is_worker(workername)
  - Type: callable method on the handler (boolean-returning)
  - Invariant: returns True if the worker name is known; False otherwise.

- self.get_argument(name)
  - Type: callable method on the handler (returns request argument value)
  - Behavior: raises tornado.web.MissingArgumentError if argument is missing.

- self.write(payload)
  - Type: callable method on the handler
  - Behavior: writes the HTTP response body. In this handler success uses dict(message=...).

- self.set_status(code)
  - Type: callable method on the handler
  - Behavior: sets HTTP response status code.

- self.error_reason(workername, response)
  - Type: callable method on the handler
  - Behavior: returns a string explanation extracted from the response object for failure messages.

- logger
  - Type: module-level logger (from logging)
  - Behavior: used to log informational and error messages.

Observed data shapes / constraints (from code):
- Request must include a 'queue' argument (string). There is no internal empty-string check; an empty queue value is forwarded as-is.
- The broadcast reply is expected to be an indexable sequence (e.g., list) where response[0] is a mapping from worker names to per-worker result objects. On success this code expects response[0][workername] to be a mapping containing an 'ok' key whose value is the success message.

Class invariants:
- post(...) will only proceed past worker validation if is_worker(workername) returns True.
- If get_argument('queue') raises MissingArgumentError, the request will fail before any broadcast is performed.
- After broadcast, the handler expects the structure response[0][workername] to exist; if not present or does not contain 'ok', the handler treats this as a failure.

## Lifecycle:
Creation:
- Instantiate via Tornado web application routing (no explicit constructor args required by this class).
- The handler is created per-request by Tornado; no persistent construction parameters are required.

Usage (typical request flow):
1. Tornado receives a POST request routed to WorkerQueueAddConsumer with a path parameter workername.
2. Tornado constructs a WorkerQueueAddConsumer instance for the request context.
3. Tornado enforces authentication because the method is decorated with @web.authenticated; unauthenticated requests are rejected before executing post.
4. post(workername) executes:
   a. Calls is_worker(workername). If False, raises tornado.web.HTTPError(404).
   b. Calls get_argument('queue') to obtain the queue name. If the argument is missing, tornado.web.MissingArgumentError is raised.
   c. Logs the intended action via logger.info.
   d. Calls self.capp.control.broadcast('add_consumer', arguments={'queue': queue}, destination=[workername], reply=True).
   e. Interprets the broadcast reply: if response and 'ok' in response[0][workername], writes dict(message=that_ok_message) to the HTTP response; otherwise logs the raw response, sets HTTP status 403, computes a failure reason via error_reason(workername, response), and writes a failure message.
5. Tornado finalizes the HTTP response and cleans up handler instance (no explicit close method required for this class).

Destruction / cleanup:
- No explicit cleanup responsibilities. Tornado will discard the handler after the request completes. Any cleanup of self.capp or broadcast resources is out-of-scope for this handler.

## Method Map:
flowchart LR
    A[POST request -> post(workername)]
    A --> B{is_worker(workername)?}
    B -- No --> C[raise HTTPError(404)]
    B -- Yes --> D[get_argument('queue')]
    D --> E[logger.info("Adding consumer...")]
    E --> F[self.capp.control.broadcast('add_consumer', arguments={'queue': queue}, destination=[workername], reply=True)]
    F --> G{response and 'ok' in response[0][workername]?}
    G -- Yes --> H[self.write(dict(message=response[0][workername]['ok']))]
    G -- No --> I[logger.error(response); self.set_status(403); reason = self.error_reason(...); self.write(f"Failed...: {reason}")]

## Raises:
Exceptions raised directly by this handler code:
- tornado.web.HTTPError(404)
  - Condition: is_worker(workername) returns False (unknown worker).
- tornado.web.MissingArgumentError (raised by get_argument)
  - Condition: the incoming request does not include the required 'queue' argument.
Notes on other possible exceptions:
- Exceptions raised by self.capp.control.broadcast (network errors, timeouts, unexpected return shapes) are not explicitly caught here and will propagate as whatever exceptions that call raises (the handler logs the raw response only for failure cases where a reply is returned but lacks the expected 'ok' result).
- The @web.authenticated decorator enforces authentication; if authentication fails, Tornado will respond with an authentication error (typically 401) and post will not be executed.

## Example:
Assume Tornado routing maps POST /workers/{workername}/queues/add to WorkerQueueAddConsumer.post.

Request:
- POST /workers/worker1/queues/add
- Form or query argument: queue=priority_tasks
- User must be authenticated (web.authenticated)

Successful flow:
- Handler confirms worker exists.
- Broadcast returns response where response[0]['worker1'] contains {'ok': "consumer added"}.
- Handler responds with HTTP 200 and JSON body: {"message": "consumer added"}

Failure flow (unknown worker):
- is_worker('workerX') -> False
- Handler raises HTTPError(404)
- Client receives 404 Not Found.

Failure flow (broadcast failed or worker returned no 'ok'):
- Broadcast returns non-success structure or no reply.
- Handler logs the raw response, sets status 403, computes a human-readable reason via error_reason(...), and responds with a plain-text failure message:
  Failed to add 'priority_tasks' consumer to 'worker1' worker: <reason>

### `flower.api.control.WorkerQueueAddConsumer.post` · *method*

## Summary:
Validate the worker, read the requested queue name from the POST body, instruct the Celery worker to add a consumer for that queue via the app control broadcast, and write an HTTP response indicating success or failure; does not return a Python value but writes to the HTTP response and may set the response status.

## Description:
This method is the HTTP POST handler invoked when an API client requests that a specific worker add a consumer for a queue. It runs in the context of a Tornado RequestHandler subclass and performs these steps:
- Validate that the named worker exists by calling self.is_worker(workername). If the worker is unknown, immediately raise a 404 HTTP error.
- Read the 'queue' argument from the POST request body or form parameters via self.get_argument('queue').
- Log an informational message and call self.capp.control.broadcast('add_consumer', ...) with destination limited to the single worker and reply=True to request a reply.
- Inspect the reply; on success write a JSON message to the response body; on failure log the raw response, set HTTP status 403, compute a human-readable reason using self.error_reason(workername, response), and write a failure message.

Known callers and invocation context:
- Invoked by Tornado's request dispatch when a POST request matches the route bound to WorkerQueueAddConsumer and supplies the workername path parameter.
- The method is decorated with @web.authenticated at the class level, so it is called only for authenticated requests (Tornado enforces this before the method runs).

Why this logic is a dedicated method:
- The method encapsulates request validation, argument parsing, the external control RPC to the worker, and coherent HTTP response writing — responsibilities that naturally belong to a single HTTP endpoint handler and should not be inlined into templates or other handlers.

## Args:
    workername (str): Worker identifier taken from the URL path parameter. Must identify a known worker according to self.is_worker.

Request arguments read:
    queue (str): Required POST/form argument retrieved via self.get_argument('queue'). Represents the queue name to add a consumer for. The method expects a non-empty string (the code does not explicitly validate emptiness beyond get_argument).

## Returns:
    None
    - The method does not return a Python value. It writes to the Tornado HTTP response using self.write(...) and may set the status code with self.set_status(...).
    - On success: writes a JSON-compatible dict-like object (dict(message=...)) containing the success message extracted from the worker reply.
    - On failure: writes a textual failure message describing why adding the consumer failed.

## Raises:
    tornado.web.HTTPError(404):
        - Raised explicitly when self.is_worker(workername) returns False with message "Unknown worker '<workername>'".
    tornado.web.MissingArgumentError (propagated):
        - If the 'queue' request argument is not present, Tornado's self.get_argument('queue') will raise a MissingArgumentError (a subclass of HTTPError) which propagates unless caught elsewhere.
    Other exceptions:
        - Exceptions raised by self.capp.control.broadcast or by self.error_reason may propagate if not handled by this method; the method itself does not wrap those calls in try/except.

## State Changes:
Attributes READ:
    self.capp           -- read to access .control.broadcast to instruct the worker.
    self (methods)      -- calls to self.get_argument, self.write, self.set_status, self.is_worker, self.error_reason are observed but are method calls (they read internal state as needed).
    logger (module-level) -- used for logging (info/error).

Attributes WRITTEN:
    None of self.<attr> fields are assigned or mutated by this method. The method does not change instance attributes (no self.some_attr = ... lines). It does mutate the HTTP response state via self.write and self.set_status (response body/status, see Side Effects).

## Constraints:
Preconditions:
    - The caller must be authenticated (the handler method is decorated with @web.authenticated).
    - workername must be recognized by self.is_worker(workername); otherwise the method will raise HTTPError(404).
    - The 'queue' request argument must be present; otherwise self.get_argument will raise a MissingArgumentError.

Postconditions:
    - On success: an HTTP response body has been written containing a JSON-like object with a "message" field extracted from the worker reply; the status defaults to 200 unless modified elsewhere.
    - On failure: HTTP status is set to 403, a textual failure message is written to the response body, and the error is logged.

## Side Effects:
    - Emits an RPC/broadcast call via self.capp.control.broadcast('add_consumer', arguments={'queue': queue}, destination=[workername], reply=True). This is a network/IPC call to Celery worker(s) and may trigger side effects on the worker (starting a consumer).
    - Writes to the HTTP response body using self.write(...).
    - May set the HTTP response status via self.set_status(403) on failure.
    - Logs information and errors via module-level logger (logger.info, logger.error).
    - May allow exceptions from Tornado or the Celery control layer to propagate (leading to framework-level error handling).

## Edge cases and implementation notes:
    - The method treats a successful reply as: response is truthy and the first item contains an entry for the workername that contains an 'ok' key (response[0][workername]['ok']). Any other reply shape is treated as failure.
    - The method relies on self.error_reason(workername, response) to produce a human-readable failure reason; that helper is invoked only in the failure path.
    - Because the method does not swallow exceptions from broadcast or helpers, callers should expect framework/error middleware to handle unexpected exceptions.

## `flower.api.control.WorkerQueueCancelConsumer` · *class*

## Summary:
Handles authenticated HTTP POST requests to cancel a queue consumer on a specific worker — validates the worker, reads the 'queue' argument, issues a control broadcast to cancel the consumer on the target worker, and returns either a success message or an error response.

## Description:
This Tornado request handler class implements a single POST endpoint used by the Flower control API to remove (cancel) a consumer for a named queue on a specific worker process.

Typical instantiation:
- Tornado creates an instance per incoming request when the routing table binds this handler class to a control API route.
- The handler is intended to be called by authenticated users (the POST method is decorated with @web.authenticated).

Why this class exists:
- Encapsulates the request-specific flow for canceling a queue consumer on a worker:
  1. Validate that the worker name provided in the URL path refers to a known worker (using ControlHandler.is_worker).
  2. Read the required 'queue' argument from request parameters.
  3. Use the application's Celery app control interface (self.capp.control.broadcast) to send a cancel_consumer command to the specified worker.
  4. Interpret the broadcast response and generate an appropriate HTTP response for the client.
- It centralizes the control-broadcast call and the success/failure response mapping for the cancel-consumer operation.

Known callers / factories:
- Tornado's request router (per-request instantiation).
- Any code that issues an HTTP POST against the route bound to this handler (for example the Flower UI or API clients).

## State:
This class defines no instance attributes of its own. It relies on inherited/request-provided state from Tornado/BaseApiHandler and the ControlHandler mixin:

- Inherited/required attributes (read-only for this handler):
  - self.application
    - Role: Tornado application instance that must expose a workers collection (used indirectly via ControlHandler.is_worker).
    - Constraint: application.workers must support membership testing ("workername in application.workers").
  - self.capp
    - Type/Role: an application-level Celery-app-like object exposing a control API at self.capp.control with a broadcast(method, arguments=..., destination=..., reply=...) function.
    - Expected behavior: broadcast(...) returns an iterable (commonly a list/tuple) of mapping-like entries describing per-destination responses.
  - self.get_argument(name, default=..., strip=...) (inherited Tornado RequestHandler method)
    - Used to retrieve the required 'queue' parameter from the request body or query string.
  - self.write(obj) and self.set_status(code) (inherited Tornado RequestHandler methods)
    - Used to return JSON-like or text responses and set HTTP status codes.
- Module-level:
  - logger (logging.Logger): used for informational and error logging.

Class invariants:
- Instances do not create or persist attributes across requests.
- Methods assume self.application and self.capp exist and behave as described above.

## Lifecycle:
Creation:
- No explicit constructor arguments required by this class; Tornado instantiates it per-request using the default handler lifecycle.

Usage (typical method sequence):
1. Tornado maps an incoming POST request with a worker name in the URL to this handler and calls post(self, workername).
2. post performs:
   - Authentication check (enforced by @web.authenticated decorator).
   - Worker validation via self.is_worker(workername).
   - Retrieval of the 'queue' argument via self.get_argument('queue').
   - Logging an informational message about the cancel operation.
   - Issuing a control broadcast via self.capp.control.broadcast('cancel_consumer', arguments={'queue': queue}, destination=[workername], reply=True).
   - Interpreting the broadcast response:
     - On success: write a JSON-like dict with the returned message.
     - On failure: log the full response, set HTTP status to 403, extract a reason using self.error_reason(workername, response), and write a human-readable failure string.
3. Tornado completes the response; the handler instance is discarded for that request.

Destruction / cleanup:
- No explicit cleanup required. No context-manager support or close() method is defined.

Sequencing constraints:
- Authentication must succeed before post executes (tornado enforces via decorator).
- self.application and self.capp must be valid before post is called; otherwise attribute access errors may occur.

## Method Map:
graph LR
    A[HTTP POST request -> post(workername)] --> B{is_worker(workername)}
    B -- false --> C[raise web.HTTPError(404)]
    B -- true --> D[get_argument('queue')]
    D --> E[logger.info("Canceling consumer ...")]
    E --> F[self.capp.control.broadcast('cancel_consumer', arguments={'queue': queue}, destination=[workername], reply=True)]
    F --> G{response and 'ok' in response[0][workername]}
    G -- true --> H[self.write({'message': response[0][workername]['ok']})]
    G -- false --> I[logger.error(response); set_status(403); reason=self.error_reason(workername,response); write(f"Failed...: {reason}")]

## Methods (detail)
post(self, workername)
- Purpose:
  - Entry point for an authenticated POST request that requests canceling a queue consumer on a specified worker.

- Inputs:
  - workername (str): Worker identifier extracted from the URL path by Tornado's routing. Must be a value that ControlHandler.is_worker can evaluate against application.workers.
  - Request body / query parameters: Expects a request argument named 'queue' accessible via self.get_argument('queue') — typically a string naming the queue to cancel.

- Behavior:
  1. Verify worker existence:
     - Calls self.is_worker(workername) (inherited from ControlHandler). If that call returns a falsy value, the method raises web.HTTPError(404, f"Unknown worker '{workername}'") immediately.
  2. Read 'queue':
     - Calls self.get_argument('queue'). If the argument is not present, Tornado raises tornado.web.MissingArgumentError (an HTTPError 400) — this handler does not catch it.
  3. Log and broadcast:
     - Logs an informational message using the module-level logger.
     - Invokes self.capp.control.broadcast('cancel_consumer', arguments={'queue': queue}, destination=[workername], reply=True).
       * Expected semantics: broadcast sends the 'cancel_consumer' control command to the listed destination worker(s) and returns a reply aggregation.
  4. Inspect the reply:
     - If the broadcast returns a truthy response and the nested mapping response[0][workername] contains an 'ok' key, write a success object dict(message=<value of ok>) back to the client (via self.write).
     - Otherwise:
       - Log the raw response at error level (logger.error(response)).
       - Set HTTP status to 403 (forbidden).
       - Compute a human-readable reason by calling self.error_reason(workername, response) and write a formatted failure string describing the problem.

- Outputs:
  - On success: writes a JSON-like object containing a 'message' key whose value is the broadcast's 'ok' payload for the worker; HTTP status remains default (200).
  - On business failure: writes a plain-text failure message and sets HTTP status to 403.
  - On invalid worker: raises web.HTTPError(404).
  - On missing 'queue' argument: tornado.web.MissingArgumentError (treated by Tornado as an HTTP 400 error) will be raised by get_argument (not handled here).

- Edge cases and constraints:
  - If self.capp or self.capp.control are missing or misbehave, attribute access will raise AttributeError.
  - The code assumes the broadcast reply is an indexable iterable and that response[0] is mapping-like with a workername key that maps to another mapping that supports key membership and indexing (so response[0][workername] must be a mapping-like object).
  - If response is an unexpected shape (e.g., empty list, list with no mapping for the worker, or non-mapping elements), expression 'ok' in response[0][workername] can raise KeyError, TypeError, or AttributeError—these are not caught inside post and will propagate, potentially resulting in an unhandled 500 response unless Tornado's error handlers intercept them.
  - The method relies on ControlHandler.error_reason to produce a fallback human-readable message when the response indicates failure; if error_reason raises due to unexpected response shape, that exception propagates.

- Side effects:
  - Emits logger.info and logger.error messages.
  - Issues a control broadcast via self.capp.control.broadcast (network/IPC side effect).

## Raises:
- web.HTTPError(404): raised explicitly when the provided workername is not known (self.is_worker returns falsy).
- tornado.web.MissingArgumentError (HTTP 400): raised by self.get_argument('queue') if 'queue' is not present in the request parameters (not caught by this handler).
- AttributeError: may be raised if required attributes are missing on the handler instance (e.g., self.capp, self.capp.control, or self.application).
- TypeError, KeyError, IndexError, AttributeError: may be raised if the broadcast response has an unexpected structure when the method attempts to index into response[0][workername] or test membership of 'ok'. These exceptions are not explicitly handled by this method.
- Any exceptions raised by self.capp.control.broadcast may propagate (network/IPC errors or library-specific exceptions).

## Example:
Scenario: A client issues an authenticated POST request to the route bound to this handler with path parameter workername='worker1' and form/body/query argument queue='tasks'.

- Expected call sequence inside Tornado:
  1. Handler receives POST request and Tornado calls WorkerQueueCancelConsumer.post(self, 'worker1').
  2. Handler validates worker1 exists via self.is_worker('worker1').
  3. Handler obtains queue = self.get_argument('queue')  -> 'tasks'.
  4. Handler logs "Canceling consumer 'tasks' from worker 'worker1'".
  5. Handler calls:
       response = self.capp.control.broadcast(
           'cancel_consumer',
           arguments={'queue': 'tasks'},
           destination=['worker1'],
           reply=True
       )
     Typical successful response shape expected by this handler:
       response == [{'worker1': {'ok': "Canceled consumer 'tasks'"}}, ...]
  6. If response is as above, the handler writes:
       {"message": "Canceled consumer 'tasks'"}
     and returns HTTP 200.
  7. If the response lacks an 'ok' entry for the worker, the handler:
     - logs the raw response,
     - sets HTTP status to 403,
     - calls self.error_reason('worker1', response) to obtain a reason string (fallbacks to 'Unknown reason' if not found),
     - writes a failure message similar to:
       "Failed to cancel 'tasks' consumer from 'worker1' worker: <reason>"

Implementation notes for re-creation:
- Implement this handler as a Tornado RequestHandler subclass that:
  - Ensures @web.authenticated is applied on post.
  - Uses self.is_worker(workername) and self.error_reason(workername, response) helpers provided by ControlHandler.
  - Expects self.capp.control.broadcast to behave as described (send remote control command and return an iterable of per-worker mappings).
- Keep in mind to validate input existence ('queue') before calling external control APIs and to handle (or document) the possible propagation of low-level exceptions when response shape is unexpected.

### `flower.api.control.WorkerQueueCancelConsumer.post` · *method*

## Summary:
Issue a control broadcast to cancel a consumer for a named queue on a specific worker, then write an HTTP response indicating success or failure. The method issues no persistent local state changes; it performs a remote control action and updates the HTTP response for this request.

## Description:
This Tornado POST handler performs the full request lifecycle for "cancel consumer" control operations:
1. Validate the worker exists via is_worker(workername).
2. Read the 'queue' POST/query argument from the request.
3. Call the application's control RPC (self.capp.control.broadcast) to request cancellation on the remote worker.
4. Inspect the aggregated broadcast response for an 'ok' result for the target worker and write a success response; otherwise log the raw response, set HTTP 403, and write a failure message constructed using error_reason.

Known callers / invocation context:
- Tornado invokes this method when a client POSTs to the route bound to WorkerQueueCancelConsumer (the class is decorated with web.authenticated, so invocation occurs only for authenticated requests).
- Typical callers are the Flower web UI or API clients that manage workers and queues.

Separation rationale:
- The logic composes request validation, argument parsing, RPC invocation, and error formatting in one place; keeping it as a dedicated method avoids repeating this control-response parsing pattern across multiple handlers.

## Args:
- workername (str)
    - Provided by Tornado as a path parameter to the handler.
    - Must be a string identifying a known worker. If it is falsy or not present in self.application.workers, the handler raises an HTTP 404 (see Raises).

Implicit request argument (extracted from the HTTP request):
- 'queue' (str)
    - Retrieved by self.get_argument('queue').
    - Must be present in the request; if it is absent, self.get_argument will raise (Tornado's MissingArgumentError is raised by get_argument in that case).

## Returns:
- The method does not return a Python value; it writes an HTTP response and sets the HTTP status:
    - Success:
        - Status: 200 (default)
        - Body: a Python dict written via self.write(dict(message=...)) where the message value is response[0][workername]['ok'] from the broadcast result.
    - Failure:
        - Status: 403
        - Body: a plain string produced as:
          "Failed to cancel '<queue>' consumer from '<workername>' worker: <reason>"
          where <reason> is the string returned by self.error_reason(workername, response).

Note: The method calls self.write with a dict on success; how that dict is serialized in the HTTP response (JSON or other) depends on the Tornado application/handler configuration.

## Raises:
- web.HTTPError(404)
    - Trigger: is_worker(workername) returns falsy (worker unknown or workername falsy). This occurs at the first two lines of the method.
- Exception from self.get_argument
    - Trigger: missing 'queue' argument. Tornado's RequestHandler.get_argument raises an exception (MissingArgumentError) when the requested argument is absent.
- Exceptions propagated from response parsing or the broadcast call
    - Possible exceptions and their direct code causes:
        - IndexError
            - Cause: response is indexable but empty (response[0] attempt).
        - KeyError
            - Cause: response[0] is a mapping but does not contain workername, or response[0][workername] is a mapping but lacks 'ok'; direct dict indexing can raise KeyError.
        - TypeError or AttributeError
            - Cause: response is not indexable (response[0] attempt raises TypeError), or response[0][workername] is not a mapping (accessing ['ok'] may raise TypeError or AttributeError if wrong type).
        - Any exception raised by self.capp.control.broadcast (network, serialization, or RPC-layer exceptions) will propagate.
    - These exceptions are not caught in this method and will be handled by Tornado's error machinery if propagated.

## State Changes:
Attributes READ:
- self.capp (used to access self.capp.control.broadcast)
- self.capp.control (method object used to invoke broadcast)
- self.application (indirectly via is_worker(workername) which inspects self.application.workers)
- self.get_argument (reads the 'queue' request parameter)
- self.error_reason (used to extract a readable error message from the broadcast response)
- module-level logger (logger.info and logger.error used for logging)

Attributes WRITTEN:
- No persistent self.<attribute> fields are modified.
- The method mutates the per-request HTTP response state via:
    - self.write(...) — writes the response body
    - self.set_status(...) — sets the HTTP response status code (called on failure)

## Constraints:
Preconditions:
- The handler instance has been created by Tornado and provided the workername path parameter.
- self.application exists and exposes a membership container self.application.workers that supports membership testing (workername in self.application.workers used by is_worker).
- self.capp and self.capp.control exist and expose a broadcast(name, arguments, destination, reply) method.

Postconditions:
- If the broadcast indicates success for the worker (the exact check in code: response and 'ok' in response[0][workername]) the handler writes a dict containing the success message and leaves the status as 200.
- Otherwise, the handler logs the full response, sets the HTTP status to 403, and writes an explanatory failure message using error_reason(workername, response).
- No persistent server-side mutable attributes on the handler object are changed.

## Side Effects:
- Calls self.capp.control.broadcast('cancel_consumer', arguments={'queue': queue}, destination=[workername], reply=True) which issues an RPC to a worker; this may cause the remote worker to cancel a consumer for the named queue.
- Logs:
    - logger.info(...) before sending the broadcast.
    - logger.error(response) when the response does not indicate success.
- Mutates the HTTP response for the request via self.write and self.set_status.
- May propagate exceptions from the broadcast call or from response parsing, which triggers Tornado's error handling for the request.

## Success condition and expected response shape:
- The implementation treats these conditions as success:
    - The variable response is truthy (e.g., non-empty), and
    - response[0][workername] exists and contains an 'ok' key.
- Expected conventional shape of broadcast response:
    - An iterable (commonly a list) where each element is a mapping from workername -> result-dict; result-dict typically contains either 'ok' or 'error'.
    - Example success fragment accessed by this method: response[0][workername]['ok'] -> success message.

## Implementation hints (for reimplementation):
- Check worker membership first and raise HTTP 404 if unknown (consistent with ControlHandler.is_worker).
- Use Tornado's RequestHandler.get_argument('queue') to read the queue name; be prepared to handle its missing-argument exception at the caller layer.
- Invoke the control broadcast with reply=True and a single-element destination list containing workername.
- Determine success exactly as: response is truthy and 'ok' is present under response[0][workername]; on success, call self.write with a dict(message=...).
- On failure, log the raw response, set HTTP 403, compute reason via error_reason(workername, response), and write the formatted failure string.

## `flower.api.control.TaskRevoke` · *class*

## Summary:
HTTP handler that revokes a Celery task identified by taskid; parses request arguments (terminate, signal), invokes the application's control revoke API, and returns a short confirmation message.

## Description:
TaskRevoke is a Tornado HTTP request handler (subclass of ControlHandler) intended to serve POST requests that revoke a running or scheduled Celery task. It is used for control endpoints in the Flower web UI or API where an authenticated client requests task revocation.

Typical instantiation/callers:
- Registered as the handler for a POST route such as /api/task/revoke/<taskid> in the Flower application routing configuration. Tornado creates an instance per request and calls the `post` method.
- Callers are HTTP clients (web UI, curl, API consumers) that issue an authenticated POST request against the route that binds taskid.

Motivation and responsibility:
- Encapsulates the simple revoke flow: parse request arguments, request the application's control layer to revoke a specified task, and respond with a human-readable confirmation.
- Delegates policy, permission checks beyond Tornado's authentication decorator, and the actual revoke implementation to the application/celery control layer. The handler does not attempt to inspect revoke results or suppress exceptions thrown by the control layer.

## State:
- logger (module-level)
  - Type: logging.Logger
  - Role: used for informational logging when a revoke is requested. Expected to be defined in the same module.
- self.capp
  - Type: application-specific object (expected to expose a .control attribute)
  - Required shape: self.capp.control must expose a method revoke(taskid, terminate=<bool>, signal=<str>)
  - Invariant: present and callable at request time; if missing, attribute access will raise AttributeError.
- Inherited state from Tornado RequestHandler / BaseApiHandler / ControlHandler:
  - self.request, self.get_argument(...) and self.write(...) are available and used by the handler.
  - Authentication enforcement is applied by the Tornado decorator @web.authenticated.

Notes on __init__ parameters:
- TaskRevoke defines no custom __init__ parameters; instances are constructed by Tornado using the standard RequestHandler lifecycle and parameters. No direct constructor args required by callers.

Class invariants:
- No instance attributes are created by TaskRevoke itself.
- Each request is handled by a freshly created instance (per Tornado semantics).
- The handler assumes self.capp and its control.revoke method are usable during the `post` invocation.

## Lifecycle:
Creation:
- Do not instantiate manually in application code. Tornado will instantiate TaskRevoke when a route maps to this handler. No constructor arguments are required beyond Tornado's usual RequestHandler signature.

Usage (typical request flow):
1. An authenticated HTTP POST request arrives at the route bound to TaskRevoke with a path parameter `taskid`.
2. Tornado performs authentication (enforced by @web.authenticated).
3. Tornado instantiates TaskRevoke for the request and calls post(self, taskid).
4. The handler:
   - Logs the revoke attempt via module-level logger.
   - Reads query/form arguments:
     - terminate: parsed via self.get_argument('terminate', default=False, type=bool)
     - signal: parsed via self.get_argument('signal', default='SIGTERM', type=str)
   - Calls self.capp.control.revoke(taskid, terminate=terminate, signal=signal).
   - Writes a response dictionary: {"message": f"Revoked '{taskid}'"} via self.write(...).
5. Tornado serializes and sends the response to the client; any exceptions raised during processing are handled by Tornado/BaseApiHandler error handling.

Destruction:
- No explicit cleanup is required. Tornado discards the handler instance after the request finishes.

## Method Map:
graph LR
    A[HTTP POST /.../<taskid>] --> B[TaskRevoke.post(taskid)]
    B --> C[logger.info("Revoking task '%s'", taskid)]
    B --> D[self.get_argument('terminate', default=False, type=bool)]
    B --> E[self.get_argument('signal', default='SIGTERM', type=str)]
    B --> F[self.capp.control.revoke(taskid, terminate, signal)]
    F --> G[self.write({"message": f"Revoked '{taskid}'"})]

## Raises:
- During __init__ / instantiation:
  - None declared by TaskRevoke. Any errors are those raised by Tornado/BaseApiHandler during request-handler initialization.
- During post(...) execution:
  - AttributeError if self.capp or self.capp.control is not present (attribute access failure).
  - Any exception raised by self.capp.control.revoke(...) (allows control-layer errors to propagate).
  - Exceptions from argument parsing:
    - If Tornado's get_argument type-casting fails (the callable provided via `type=` raises), that exception will propagate.
    - MissingArgumentError is not expected here because defaults are provided; however, malformed types could still raise.
  - If the client is not authenticated, the @web.authenticated decorator prevents invocation of post and causes Tornado to respond with the configured authentication response (e.g., redirect or 403); exact behavior is determined by the application's authentication setup.

## Example:
Scenario: revoke a task with id "abc123", terminate immediately and send SIGKILL.

HTTP request (illustrative):
- Method: POST
- URL: /api/task/revoke/abc123
- Query/form parameters:
  - terminate=true
  - signal=SIGKILL
- Authentication: required (handled by Tornado/web.authenticated)

Handler behavior:
1. Tornado invokes TaskRevoke.post(self, taskid="abc123").
2. The handler logs: Revoking task 'abc123'
3. terminate is obtained via self.get_argument('terminate', default=False, type=bool)  (value -> True)
4. signal is obtained via self.get_argument('signal', default='SIGTERM', type=str)  (value -> 'SIGKILL')
5. Calls self.capp.control.revoke('abc123', terminate=True, signal='SIGKILL')
6. Responds with JSON-like body: {"message": "Revoked 'abc123'"} or appropriate error if revoke failed.

Notes:
- The handler does not inspect the return value of control.revoke; failures in revoke will propagate and be handled by the application's error handling.
- Ensure that the application wiring provides self.capp with a control.revoke callable before exposing this endpoint.

### `flower.api.control.TaskRevoke.post` · *method*

## Summary:
Handles an HTTP POST request to revoke a Celery task identified by the URL path parameter; it parses revoke options from request arguments, calls the Celery control revoke API, logs the action, and writes a small JSON confirmation to the HTTP response.

## Description:
This method is the Tornado RequestHandler POST entry point invoked by the Tornado routing machinery when a POST request is sent to the route mapped to this handler (i.e., the lifecycle stage where an HTTP client requests task revocation). It is decorated with web.authenticated, so Tornado enforces authentication before this method runs.

It exists as a dedicated method because revoking a task is an independent HTTP operation that:
- needs to parse and validate request arguments (terminate and signal),
- perform an external control action using the configured Celery application,
- produce a JSON confirmation response and log the operation.

Keeping this logic in one method centralizes request parsing, authorization boundary, Celery control invocation, and response formatting.

Known callers / invocation context:
- Tornado's RequestHandler dispatch: when a POST request reaches the route mapped to TaskRevoke, Tornado calls TaskRevoke.post(self, taskid) with taskid extracted from the URL.
- The web.authenticated decorator checks authentication before this method executes; if unauthenticated, Tornado will raise an HTTP 401 and this method will not run.

Why separate:
- Clear separation of HTTP handling and Celery control operations; allows routing, authentication, and request-parsing responsibilities to be colocated for this single endpoint.

## Args:
    taskid (str): Task identifier extracted from the request URL. Expected to be a non-empty string; Tornado provides the path segment as a string.

Request arguments parsed inside the method (via BaseHandler.get_argument):
    terminate (bool): Optional query/body parameter. Parsed with type=bool, default False.
        - Conversion uses BaseHandler.get_argument behavior: if provided as a string, values recognisable by strtobool (e.g., "true", "1", "yes") will be converted to True/False. If conversion fails, a tornado.web.HTTPError(400) is raised.
    signal (str): Optional query/body parameter. Parsed with type=str, default 'SIGTERM'.
        - Conversion to str is applied; since default is a str, omission returns 'SIGTERM'.

Notes on how arguments are obtained:
- Arguments are retrieved via BaseHandler.get_argument(name, default=..., type=...), which performs HTML-escaping for string values and performs type conversion. For bool conversion it uses strtobool via BaseHandler.get_argument.

## Returns:
    None

Behavioral result visible to the caller:
    - On successful execution the method writes a JSON-serializable dictionary to the HTTP response body: {"message": "Revoked '<taskid>'"} (single-quoted taskid inside the string).
    - The Tornado RequestHandler.write is called with that dict; Tornado will serialize it according to its conventions (commonly to JSON when the client expects JSON).

Edge-case return behavior:
    - The method itself returns None to Tornado; the meaningful output is the HTTP response body written via self.write.

## Raises:
    tornado.web.HTTPError(401)
        - Triggered by the web.authenticated decorator (if the request is not authenticated). This happens before this method executes.
    tornado.web.HTTPError(400)
        - Raised by BaseHandler.get_argument when an argument cannot be converted to the requested type (e.g., an invalid boolean string for terminate). The exact error is raised when converting the provided argument to the requested type fails.
    Any exception raised by self.capp.control.revoke(...)
        - The method does not catch exceptions from the Celery control API. Errors thrown by the Celery client (e.g., communication errors) will propagate and ultimately result in a 500 error unless handled by upstream middleware/handlers.

## State Changes:
Attributes READ:
    self.capp
        - Accessed via the BaseHandler.capp property to obtain the Celery application object. This in turn reads self.application.capp.
    (indirectly) request arguments via self.get_argument
        - The method calls get_argument to read request parameters; this reads request state but is not a persistent attribute on self.

Attributes WRITTEN:
    None of the handler's persistent attributes are mutated.
    (Effect on handler state)
        - The method calls self.write(...) which mutates the handler's response buffer / outgoing HTTP response body (internal handler state used by Tornado). This is a side-effect on the HTTP response, not a persistent attribute like self.foo.

## Constraints:
Preconditions:
    - The HTTP request must be authenticated (enforced by web.authenticated) or else a 401 is returned and this method will not run.
    - The taskid path parameter must be present (provided by the routing system) and is expected to be a string.
    - If present, the terminate argument must be convertible to bool by BaseHandler.get_argument; otherwise a 400 HTTPError is raised.
    - The application must have a configured Celery app available at self.application.capp (BaseHandler.capp property).

Postconditions:
    - If execution completes without exception:
        - self.capp.control.revoke(taskid, terminate=terminate, signal=signal) has been invoked (Celery has been instructed to revoke the specified task with the provided options).
        - The HTTP response body contains {"message": "Revoked '<taskid>'"} and the response will be sent to the client by Tornado.
    - If self.capp.control.revoke raises, the revoke request may not have taken effect; the exception propagates.

## Side Effects:
    - External service call: Invokes the Celery control API via self.capp.control.revoke(taskid, terminate=terminate, signal=signal). This sends a revoke command to Celery workers/transport and may cause the task to be revoked or terminated depending on options and worker state.
    - Logging: Writes an INFO-level log entry via logger.info("Revoking task '%s'", taskid).
    - HTTP response mutation: Calls self.write(...) to add the JSON confirmation to the outgoing HTTP response.

## Implementation notes / reimplementation guidance:
    - Ensure the method is decorated with web.authenticated to enforce authentication at the Tornado level.
    - Parse request arguments using the same semantics as BaseHandler.get_argument:
        * terminate should be parsed with default False and boolean conversion that accepts common truthy/falsey strings.
        * signal should be parsed as a string with default 'SIGTERM', escaping HTML for safety if strings come from untrusted sources.
    - Use the application's Celery app object (self.application.capp) and call control.revoke(taskid, terminate=terminate, signal=signal).
    - Log the revoke attempt before invoking the Celery API.
    - Write a JSON-serializable confirmation dictionary to the response body after invoking revoke; do not swallow exceptions from the Celery call unless higher-level behavior requires mapping them to user-friendly HTTP responses.

## `flower.api.control.TaskTimout` · *class*

*No documentation generated.*

### `flower.api.control.TaskTimout.post` · *method*

## Summary:
Handles an HTTP POST that sets soft and/or hard timeouts for a named task; validates the task and optionally the target worker, sends a time_limit control command through the app control interface, and writes an HTTP response indicating success or failure.

## Description:
This method is invoked to process an incoming HTTP POST request aimed at setting timeout limits for a specific Celery task. Typical caller/context:
- Tornado request handling pipeline when an HTTP POST is issued against the TaskTimout endpoint (i.e., this method is the POST handler of a RequestHandler subclass).
- Lifecycle stage: request handling / control-plane operation to change runtime task timeout configuration.

Why this logic is a separate method:
- It implements a single, discrete HTTP endpoint behavior: validate request parameters, call the centralized control API (self.capp.control.time_limit), and produce an HTTP response. Keeping it as a dedicated handler method isolates request parsing, validation, control-plane interaction, and HTTP response logic.

## Args:
    taskname (str):
        The name (string key) of the task whose timeouts will be changed. It must be present in self.capp.tasks (otherwise a 404 HTTPError is raised).

Note: request parameters (obtained from the HTTP request) read inside the method:
    workername (str | None):
        Retrieved from the request arguments via self.get_argument('workername'). When provided and not matching a known worker, a 404 HTTPError is raised. The method treats an explicitly provided workername as the destination for the control command; if not provided (i.e., no destination specified), the control command is broadcast/unspecified destination (destination is None).
    hard (float | None):
        Retrieved from the request arguments via self.get_argument('hard', default=None, type=float). Represents the hard timeout value to set; may be None meaning "do not change".
    soft (float | None):
        Retrieved from the request arguments via self.get_argument('soft', default=None, type=float). Represents the soft timeout value to set; may be None meaning "do not change".

## Returns:
    None
    - The method does not return a Python value; it writes an HTTP response using self.write(...) and sets an HTTP status when necessary.
    - On success: writes a JSON-like dict with a "message" key extracted from the control response (status code remains the handler's default, typically 200).
    - On failure: sets HTTP status 403 and writes a plain-text failure message describing the reason.

## Raises:
    web.HTTPError(404):
        - If taskname is not present in self.capp.tasks: raised with message "Unknown task '<taskname>'".
        - If workername is provided (not None) and self.is_worker(workername) returns false: raised with message "Unknown worker '<workername>'".
    Note: the method does not explicitly raise other exceptions in the shown code path, but underlying calls (e.g., self.get_argument, self.capp.control.time_limit) may raise their own exceptions which are not handled here.

## State Changes:
Attributes READ:
    - self.capp.tasks: used to validate that taskname is known.
    - self.capp.control.time_limit: invoked to request setting time limits (control-plane RPC/command).
    - self.get_argument(...): called to read request arguments workername, hard, and soft.
    - self.is_worker(workername): called to validate provided workername.
    - self.error_reason(taskname, response): called to extract a human-readable reason when the control response indicates failure.
    - self.write(...): invoked to write the HTTP response body.
    - self.set_status(...): invoked to set HTTP response status code when the operation fails.
    - logger (module-level): logger.info and logger.error are called for audit/logging.

Attributes WRITTEN:
    - The method does not assign to any self.<attribute> fields in the snippet. It does mutate the HTTP response state by calling self.write(...) and self.set_status(...), which are side-effecting methods on the RequestHandler/response, not attribute assignments shown in the snippet.

## Constraints:
Preconditions:
    - taskname must be a string key that exists in self.capp.tasks; otherwise the method immediately raises web.HTTPError(404).
    - If the request includes a workername (as obtained from self.get_argument), that workername must be recognized by self.is_worker(workername) or the method raises web.HTTPError(404).
    - soft and hard, if present in the request, will be converted to float via self.get_argument(..., type=float); conversion errors are propagated by get_argument.

Postconditions:
    - If the underlying control call returns a response in the expected shape and indicates success for the targeted worker (the code checks response and 'ok' in response[0][workername]), the method writes a JSON-like dict { "message": <success message> } to the response body.
    - If the response is missing, malformed, or does not contain the expected success marker, the method logs the raw response, sets the HTTP status to 403, computes a human-readable reason via self.error_reason(taskname, response), and writes a failure message string into the body.

## Side Effects:
    - I/O / external RPC: calls self.capp.control.time_limit(...), which is a control-plane command that may perform RPC to worker(s) or other external systems.
    - HTTP response side effects: calls self.write(...) to emit the response body and self.set_status(403) when the operation fails.
    - Logging: emits an INFO log indicating the requested timeout values and an ERROR log printing the raw response on failure.
    - Potentially raises tornado.web.HTTPError(404) as described above, which affects the HTTP response lifecycle handled by Tornado.

## `flower.api.control.TaskRateLimit` · *class*

## Summary:
Tornado request handler that processes POST requests to set a rate limit for a specific task on a specific worker by validating inputs and calling the application's control.rate_limit API; returns a success message on OK or a descriptive error on failure.

## Description:
TaskRateLimit.post handles HTTP POST requests intended to configure a task's rate limit through Flower's control API. It expects the task name as the URL path parameter (taskname) and two request arguments:

- workername (required): identifier of the worker to target (string). In the current implementation this argument is retrieved with get_argument('workername') without a default, so it must be present in the request; Tornado will raise web.MissingArgumentError if it is omitted.
- ratelimit (required): rate limit specification (string). This value is passed through verbatim to the control API; the handler performs no validation of its format.

Responsibilities:
- Verify the named task exists in self.capp.tasks.
- Verify the provided workername is known via ControlHandler.is_worker.
- Invoke self.capp.control.rate_limit(taskname, ratelimit, reply=True, destination=destination) with destination set to [workername].
- If the control API returns a positive acknowledgement, write a JSON-like success payload (dict with message).
- On control failure, log the raw response, set the HTTP status to 403, compute a readable reason via ControlHandler.error_reason, and write a failure string.

Authentication:
- The method is decorated with web.authenticated; callers must be authenticated per the application's auth policy. Unauthenticated requests are handled by Tornado / the application's auth layer (e.g., redirect or web.HTTPError depending on configuration).

Motivation:
- Encapsulates HTTP-to-control semantics for rate-limiting a task on a worker, centralizing validation, logging, and response translation for the API endpoint.

## State:
Accessed attributes (expected to exist at runtime)
- self.capp
  - self.capp.tasks: mapping-like container of valid task names; membership tested with "taskname in self.capp.tasks".
  - self.capp.control.rate_limit: callable invoked to perform the rate limit change.
- ControlHandler helpers (inherited):
  - self.is_worker(workername): verifies worker membership; may return truthy/falsey per implementation.
  - self.error_reason(workername, response): extracts a human-readable error from a control response iterable.
- Tornado RequestHandler methods:
  - self.get_argument(name): reads request argument; raises web.MissingArgumentError if absent.
  - self.write(payload): emits response body.
  - self.set_status(code): sets HTTP response status.
- module-level logger (logger): used for info and error logging.

Valid values / invariants:
- taskname: must be a key in self.capp.tasks.
- workername: must be present in the request and must pass self.is_worker(workername).
- ratelimit: any string; validation is delegated to the control API or callers.
- Class invariant: the handler assumes self.capp and the control API exist and conform to the expected interfaces; absent attributes will cause AttributeError.

Important implementation note (current-code caveat):
- The handler reads workername with get_argument('workername') which requires the client to supply the parameter. The code then checks "if workername is not None and not self.is_worker(workername):" — but get_argument will not return None when the parameter is missing (it raises an error), so the check does not make workername optional. If optional worker targeting (broadcast) was intended, the implementation should use get_argument('workername', default=None). As written, workername effectively must be provided.

## Lifecycle:
Creation:
- Instantiated per-request by Tornado when a route maps a POST path with a taskname parameter to TaskRateLimit.

Usage sequence (typical POST):
1. Tornado invokes TaskRateLimit.post(self, taskname).
2. The method calls self.get_argument('workername') and self.get_argument('ratelimit'). Missing arguments cause web.MissingArgumentError.
3. Validate task membership: if taskname not in self.capp.tasks → raise web.HTTPError(404).
4. Validate worker: if not self.is_worker(workername) → raise web.HTTPError(404).
5. Log intent: logger.info("Setting '%s' rate limit for '%s' task", ratelimit, taskname).
6. destination = [workername] (the current code never routes a broadcast because workername is required).
7. response = self.capp.control.rate_limit(taskname, ratelimit, reply=True, destination=destination)
8. If response and response[0][workername] contains 'ok', write dict(message=response[0][workername]['ok']) and return HTTP 200.
9. Else, logger.error(response); self.set_status(403); reason = self.error_reason(taskname, response); write failure message.

Destruction:
- Tornado discards the handler after request processing. No custom cleanup is required.

## Method Map:
graph LR
    POST_request --> A[get_argument('workername'), get_argument('ratelimit')]
    A --> B{taskname in self.capp.tasks?}
    B -- no --> C[raise web.HTTPError(404, "Unknown task")]
    B -- yes --> D{is_worker(workername)?}
    D -- no --> E[raise web.HTTPError(404, "Unknown worker")]
    D -- yes --> F[logger.info(...); destination=[workername]]
    F --> G[self.capp.control.rate_limit(taskname, ratelimit, reply=True, destination)]
    G --> H{response and 'ok' in response[0][workername]?}
    H -- yes --> I[self.write(dict(message=response[0][workername]['ok']))]
    H -- no --> J[logger.error(response); set_status(403); write failure with error_reason]

## Raises:
Explicitly raised by this handler:
- web.HTTPError(404, f"Unknown task '{taskname}'")
  - When: taskname not found in self.capp.tasks.
- web.HTTPError(404, f"Unknown worker '{workername}'")
  - When: workername provided but self.is_worker(workername) returns falsy.

From Tornado request argument handling:
- web.MissingArgumentError (subclass of web.HTTPError)
  - When: either 'workername' or 'ratelimit' is omitted from the request (because get_argument is used without defaults).

Implicit runtime errors that may propagate:
- AttributeError if self.capp, self.capp.tasks, or self.capp.control is missing.
- Any exception raised by self.capp.control.rate_limit (network/IPC errors, etc.).
- IndexError, KeyError, TypeError, or AttributeError when inspecting the response:
  - The code indexes response[0][workername] and then checks for 'ok' in that mapping. If response is empty, response[0] raises IndexError. If response[0] lacks workername, KeyError occurs. If response[0][workername] is not a mapping, membership test and indexing may raise TypeError/AttributeError.

Behavior on control failure:
- If the response does not match the success condition, the handler:
  - Logs the raw response at error level.
  - Sets HTTP status to 403.
  - Uses ControlHandler.error_reason(taskname, response) to compute a human-readable reason and writes "Failed to set rate limit: '<reason>'".

## Response shape expectations:
- response is expected to be a non-empty iterable (commonly a list) whose first element is a mapping keyed by worker names.
- The value response[0][workername] is expected to be a mapping-like object that may contain:
  - 'ok' : success message/value (used by the handler)
  - 'error' : error message (used by ControlHandler.error_reason)

## Example:
HTTP POST to /api/tasks/<taskname>/ratelimit with form/query arguments:
- workername=worker1@example.com
- ratelimit=10/s

Server-side flow:
1. post(taskname='tasks.add') retrieves workername and ratelimit.
2. Validates 'tasks.add' ∈ self.capp.tasks.
3. Validates self.is_worker('worker1@example.com') is truthy.
4. Calls self.capp.control.rate_limit('tasks.add', '10/s', reply=True, destination=['worker1@example.com']).
5. If control returns: [{'worker1@example.com': {'ok': 'rate set to 10/s'}}]
   - Response body: {"message": "rate set to 10/s"} (HTTP 200)
6. If control returns: [{'worker1@example.com': {'error': 'invalid format'}}]
   - Handler logs the response, sets HTTP status 403 and writes:
     Failed to set rate limit: 'invalid format'

Implementation note for maintainers:
- If the intended behavior is to allow broadcasting a rate limit to all workers (i.e., make workername optional), change the argument retrieval to self.get_argument('workername', default=None) and adapt the response-handling logic to iterate or aggregate results when destination is None. As written, workername is required and destination is always a single-item list.

### `flower.api.control.TaskRateLimit.post` · *method*

## Summary:
Handles an authenticated HTTP POST that sets a Celery task's rate limit by invoking the application control API and writing an HTTP response indicating success or failure.

## Description:
This method is an HTTP handler invoked by the Tornado web server when a client issues a POST request to the route bound to TaskRateLimit (the route typically includes the task name as a path parameter). Typical callers are:
- The Flower web UI when an operator sets a new rate limit for a task.
- External clients calling the Flower REST API to adjust task rate limits.

It is implemented as its own method because it is a discrete HTTP endpoint: it performs argument extraction and validation, invokes the app-level control API (self.capp.control.rate_limit) to effect the change, and formats the HTTP response (success message or failure with status code) — concerns that belong in the request handler rather than inlined into templates or control logic.

## Args:
    taskname (str):
        - The target task name (provided as the URL path parameter).
        - Must be the name of a registered task in self.capp.tasks.

HTTP POST body / query parameters (read via RequestHandler.get_argument):
    workername (str | None):
        - Optional. The worker identifier to which the rate limit should apply.
        - If present, must identify a known worker according to self.is_worker(workername).
        - If omitted, the handler will request the control API without a specific destination (broadcast/global), but behavior then depends on the control API and response structure.
        - Note: get_argument will raise tornado.web.MissingArgumentError if the parameter is absent and no default is provided; the code reads both 'workername' and 'ratelimit' without defaults.

    ratelimit (str):
        - Required. A string describing the rate limit to apply (passed unchanged to self.capp.control.rate_limit).
        - Typical formats are those accepted by Celery control.rate_limit (for example, "10/m"), but the method does not validate format itself.

## Returns:
    None
    - The method does not return a Python value; it writes an HTTP response via self.write().
    - On success: writes a JSON-like dict containing the control API's OK message, e.g. {"message": "<ok-text>"} and leaves the HTTP status at the default (200).
    - On failure (control API indicates failure or response structure is not as expected): sets HTTP status 403 and writes a plain-text failure message "Failed to set rate limit: '<reason>'".
    - On unknown task or unknown worker: raises an HTTP 404 (see Raises).

## Raises:
    web.HTTPError(404)
        - Raised when taskname is not present in self.capp.tasks: "Unknown task '<taskname>'".
        - Raised when workername is provided but self.is_worker(workername) returns False: "Unknown worker '<workername>'".

    tornado.web.MissingArgumentError (propagated)
        - If 'workername' or 'ratelimit' arguments are missing from the POST/query parameters and Tornado's RequestHandler.get_argument enforces presence (no default provided), that MissingArgumentError will propagate.

    KeyError / IndexError (possible)
        - The code indexes response[0][workername] without robust existence checks; if the control API returns an unexpected structure (missing index 0 or missing the workername key) this may raise KeyError or IndexError and surface as a 500 server error. The current implementation does not catch these exceptions.

## State Changes:
Attributes READ:
    - self.capp
        * self.capp.tasks (checked for membership of taskname)
        * self.capp.control (used to call rate_limit)
    - self.is_worker(workername) (method call used for worker validation)
    - self.error_reason(taskname, response) (called to build human-readable failure reason)
    - Tornado RequestHandler methods:
        * self.get_argument('workername')
        * self.get_argument('ratelimit')

Attributes WRITTEN:
    - None of the handler's persistent attributes are modified by this method.
    - The HTTP response state is modified via:
        * self.write(...) — writes body content
        * self.set_status(403) — sets HTTP response status on failure

## Constraints:
Preconditions:
    - The request must be authenticated (enforced by @web.authenticated on the method).
    - self.capp must be initialized and expose:
        * a mapping-like attribute .tasks containing registered task names
        * a .control object exposing a rate_limit method callable as used
    - taskname must be a string present in self.capp.tasks.
    - If workername is provided, self.is_worker(workername) must return True.

Postconditions:
    - If the control API returns a response containing an 'ok' entry indexed by the worker name (response[0][workername]['ok']), the method writes a JSON object with that ok message and leaves the status as 200.
    - Otherwise, the method logs the raw response, sets HTTP status to 403, computes a failure reason using self.error_reason(taskname, response), and writes a failure message to the body.
    - If precondition checks fail (unknown task or unknown worker), a 404 HTTPError is raised and no control API call is made.

## Side Effects:
    - Calls external control API: self.capp.control.rate_limit(taskname, ratelimit, reply=True, destination=destination). This triggers control-plane communication (to workers or the broker) and may have distributed effects (setting worker or task rate limits).
    - Logs operations and failures via module-level logger (logger.info and logger.error).
    - Writes to the HTTP response body and (on failure) sets the response status code, affecting the observed HTTP response returned to the client.

## Implementation notes and edge cases:
    - The method forwards the ratelimit string directly to the control API and performs no format validation.
    - The code expects response to be indexable as response[0][workername]; if the response structure differs (e.g., broadcast responses keyed differently or workername is None), the indexing may raise exceptions. Callers should ensure the control API's reply format matches this expectation or the handler should be hardened to validate response shape.
    - The method intentionally treats missing/unknown worker as a 404 for clarity to API clients; control API failures map to a 403 response from this handler.

