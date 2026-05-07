# `workers.py`

## `flower.api.workers.ListWorkers` · *class*

## Summary:
HTTP GET request handler that lists worker information for the Flower application; supports refreshing worker list, returning liveness status, and filtering by worker name.

## Description:
ListWorkers is a Tornado request handler (subclass of ControlHandler) that responds to authenticated HTTP GET requests on the control API that enumerate workers. It is intended to be instantiated and executed per-request by Tornado when the Flower web application routes a GET request to this handler.

Typical scenarios:
- A client requests the current known workers (no query parameters).
- A client requests the alive status of each worker (status=true).
- A client requests a single worker's data (workername=<name>).
- A client requests the server to refresh its view of workers from remote sources before returning results (refresh=true).

Known callers / factories:
- Tornado routing infrastructure creates instances of this handler per HTTP request. No factory methods are defined on this class. The web route configuration in the Flower application registers this handler for the relevant API endpoint.

Motivation and responsibility boundary:
- Separates the HTTP-level parsing and response formatting of worker-list operations from lower-level application logic (e.g., inspection/update of workers). This handler coordinates request arguments, triggers (optional) refresh operations, and selects which worker information is returned to the HTTP client. It delegates worker discovery and state to self.application and uses ControlHandler utilities (e.g., is_worker).

## State:
This class defines no instance attributes of its own. It relies on inherited request-handler state and module-level variables:

- Methods / attributes referenced at runtime (provided by environment/inheritance):
  - self.get_argument(name, default=..., type=...): Tornado RequestHandler helper to read query parameters.
    - Used parameters:
      - 'refresh' (default False, type bool)
      - 'status' (default False, type bool)
      - 'workername' (default None) — expected string or None
  - self.application: Flower application object. Expected members used by this handler:
    - application.update_workers(workername=None) -> awaitable(s)
      - Called when refresh is requested to refresh worker information from the inspector/remote sources.
      - The handler awaits asyncio.wait(...) on its return value; thus update_workers must return an awaitable or an iterable of awaitables/futures.
    - application.workers: mapping-like container keyed by worker name -> worker-info-object.
      - May be empty or missing keys; membership test (workername in application.workers) is used.
      - Values are returned directly via self.write(...)
    - application.events.state.workers: mapping-like container keyed by worker name -> worker-object
      - Each worker-object is expected to have an 'alive' attribute used when status=True.
  - self.write(value): Tornado RequestHandler method used to produce the response body. This handler writes dict-like objects (mapping workername -> data) or the whole application.workers mapping.
  - self.is_worker(workername): From ControlHandler; used to validate whether a worker is known.

- Module-level logger:
  - The handler logs update failures with logger.error(...). The module must define a logger variable (commonly logging.getLogger(__name__)) for error logging.

Class invariants:
- Instances assume self.application exists and exposes the expected attributes (update_workers, workers, events.state.workers). If these are missing, attribute access will raise errors at runtime.
- The handler does not mutate global application state except via awaiting application.update_workers (which may have side effects defined elsewhere).

## Lifecycle:
Creation:
- Instantiated per-request by Tornado. No explicit constructor parameters are required by the class itself; Tornado supplies the usual handler constructor arguments.

Usage (typical sequence within a single GET request):
1. Authentication: The method is decorated with web.authenticated; Tornado's authentication machinery will enforce access before get() runs.
2. Parse query arguments:
   - refresh: boolean flag requesting a refresh from the inspector/backend. Default False.
   - status: boolean flag requesting only alive-status per worker. Default False.
   - workername: optional string to filter to a single worker. Default None.
3. If refresh is truthy:
   - Calls application.update_workers(workername=workername) and awaits it via await asyncio.wait(...).
   - On exception: logs via logger.error(...) and raises web.HTTPError(503, msg) to signal service-unavailable.
4. If status is truthy:
   - Builds a mapping {workername: worker.alive} by iterating self.application.events.state.workers and writes that mapping as the response body, then returns immediately.
5. If not status:
   - If application.workers is truthy, refresh is False, and workername is present in application.workers:
     - Writes a single-entry mapping {workername: application.workers[workername]} and returns.
   - Else, if a workername is provided but is not recognized by is_worker(workername):
     - Raises web.HTTPError(404, f"Unknown worker '{workername}'")
   - Else, if workername is provided:
     - Writes {workername: application.workers[workername]} (may raise KeyError if application.workers lacks the key; prior is_worker check prevents this in normal runs).
   - Else (no workername):
     - Writes the full application.workers mapping.

Destruction:
- No explicit cleanup required. Tornado discards the handler instance after request completion.

Concurrency and async notes:
- get() is declared async and uses await asyncio.wait(...). Wait is used to wait on update_workers; callers must ensure update_workers returns an awaitable or an iterable of awaitables. The handler catches any exception raised during that operation and converts it into an HTTP 503 error.

## Method Map:
graph LR
    A[HTTP GET (authenticated)] --> B[get:parse args]
    B --> C{refresh?}
    C -- yes --> D[await asyncio.wait(application.update_workers(...))]
    D --> E{exception?}
    E -- yes --> F[logger.error & raise HTTPError(503)]
    E -- no --> G{status?}
    C -- no --> G
    G -- yes --> H[collect alive statuses from application.events.state.workers]
    H --> I[self.write(status mapping) & return]
    G -- no --> J{workername specified and workername in application.workers and not refresh?}
    J -- yes --> K[self.write(single worker mapping) & return]
    J -- no --> L{workername specified and not is_worker(workername)?}
    L -- yes --> M[raise HTTPError(404)]
    L -- no --> N{workername specified?}
    N -- yes --> O[self.write({workername: application.workers[workername]})]
    N -- no --> P[self.write(application.workers)]

## Raises:
- web.HTTPError(503, msg)
  - Trigger: application.update_workers(...) raised an exception during the refresh operation. The handler logs the original exception and raises a 503 Service Unavailable with message "Failed to update workers: <original-exception>".
- web.HTTPError(404, "Unknown worker '<name>'")
  - Trigger: A workername query parameter was provided and ControlHandler.is_worker(workername) returned a falsy (not recognized) result.
- RuntimeAttributeError / KeyError / TypeError (not explicitly raised by handler but possible):
  - If self.application or expected sub-attributes (update_workers, workers, events.state.workers) are missing, attribute access may raise AttributeError.
  - If application.workers lacks a requested worker but is_worker incorrectly returns True (or application state changed between the is_worker check and access), a KeyError may occur.
  - If application.update_workers returns unexpected non-awaitable values, awaiting/waiting on them may raise TypeError.

## Example:
Consider these HTTP GET request examples (handler is authenticated by Tornado):

1) List all workers (no query params)
Request:
    GET /api/workers
Behavior:
    - Parse arguments: refresh=False, status=False, workername=None
    - Writes the full application.workers mapping as the response body.

2) Return alive status for all workers
Request:
    GET /api/workers?status=true
Behavior:
    - If status is truthy, builds {name: worker.alive} from application.events.state.workers
    - Writes that mapping and returns immediately.

3) Refresh worker list for a specific worker and return that worker
Request:
    GET /api/workers?refresh=true&workername=worker@host
Behavior:
    - Calls await asyncio.wait(application.update_workers(workername="worker@host"))
    - On success, if application.workers contains 'worker@host' writes { 'worker@host': application.workers['worker@host'] }
    - On failure, logs and raises HTTP 503 with a "Failed to update workers: ..." message.

4) Request an unknown worker
Request:
    GET /api/workers?workername=nonexistent@host
Behavior:
    - If is_worker('nonexistent@host') is falsy, raises HTTP 404 with message "Unknown worker 'nonexistent@host'".

Notes for implementers:
- Ensure the application object provided to the handler exposes update_workers, workers, and events.state.workers as described; the handler does not create or validate these structures beyond membership checks.
- Ensure a module-level logger exists (logger.error is called on update failure).
- The handler delegates authentication to Tornado via the web.authenticated decorator; make sure Tornado authentication is configured for the route.

### `flower.api.workers.ListWorkers.get` · *method*

## Summary:
Handle an HTTP GET request for worker information, optionally refreshing backend worker state or returning only liveness status; writes a JSON-mappable dict to the HTTP response stream and does not return a Python value.

## Description:
This asynchronous handler method is invoked by Tornado to service an incoming GET request routed to the ListWorkers endpoint (typically the /api/workers or equivalent control API used by the Flower web UI or API clients). Typical callers:
- Tornado's request dispatch machinery when a client issues an authenticated HTTP GET to the route associated with ListWorkers.
- Internal UI code or API consumers requesting worker listings, per-worker details, or liveness status.

This logic is kept as a dedicated method because it is the HTTP GET lifecycle hook for this route: it performs argument parsing, optionally triggers an asynchronous refresh operation, selects one of several response shapes (status-only, single-worker, or full listing), and is responsible for writing the HTTP response and raising appropriate HTTP errors. Keeping it as a method preserves the request-handler lifecycle, integrates with Tornado's authentication decorator, and cleanly separates HTTP handling from application-level worker management logic.

## Args (query parameters; read from the request):
    refresh (bool): If True, initiate an update of worker information from the application layer before producing the response. Default: False.
    status (bool): If True, respond with a mapping of worker names to their liveness (boolean) instead of full worker metadata. Default: False.
    workername (str | None): If provided, limit the response to the named worker. Default: None.

Note: These are parsed using Tornado's get_argument with the exact names 'refresh', 'status', and 'workername'; type conversion follows the get_argument(type=...) behavior (code uses type=bool for 'refresh' and 'status').

## Returns:
    None (the method writes the response via the request handler's write method).
    Possible written response bodies (JSON-mappable Python objects):
      - If status=True:
          dict[str, bool] mapping each known worker name to the worker.alive boolean.
      - If workername is provided and exists:
          dict[str, Any] with a single key equal to workername and a value taken from self.application.workers[workername] (the application-provided worker metadata/object).
      - Otherwise:
          self.application.workers (mapping-like object) is written as-is; typically dict[str, Any] mapping worker names to metadata.
    Edge cases:
      - If there are no known workers, an empty dict is written.
      - The Python method itself returns None; the HTTP response body is produced by self.write.

## Raises:
    web.HTTPError(503): Raised if refresh=True and awaiting the application's update_workers task raises any exception. The exception message is included in the HTTPError message and an error is logged.
    web.HTTPError(404): Raised when a workername is supplied but the name is not recognized by is_worker(workername).
    AttributeError/KeyError/TypeError: May propagate if expected application attributes (application.update_workers, application.workers, application.events.state.workers) or worker objects are missing or malformed. These are not explicitly caught in this method.

## State Changes:
Attributes READ:
    - self.application (used to access):
        - self.application.update_workers (called when refresh=True)
        - self.application.workers (read to build per-worker or full responses)
        - self.application.events.state.workers (read when status=True to compute liveness)
    - self.get_argument (request parsing helper)
    - self.is_worker (ControlHandler helper used to validate worker existence)
    - logger (module-level) for logging update failures
Attributes WRITTEN:
    - No instance attributes on self are modified.
    - External state mutated via awaited call:
        - application.update_workers(...) may mutate application.workers or application.events; those mutations are performed by the application code invoked and are not internal to this method.
    - I/O side-effect:
        - The HTTP response stream via self.write(...) is written with the resulting mapping.

## Constraints:
Preconditions:
    - The request must be authenticated (the class decorator enforces authentication; the method assumes the decorator has run).
    - self.application must expose:
        - a callable update_workers(workername=...) that returns awaitable(s) or an iterable of awaitables consumable by asyncio.wait.
        - a mapping-like application.workers supporting membership testing and indexing by worker name.
        - application.events.state.workers mapping where values have an .alive attribute when status=True is used.
    - Tornado RequestHandler methods get_argument(...) and write(...) must be available on self (inherited behavior).

Postconditions:
    - One of the following responses has been written to the HTTP response stream:
        - liveness mapping (name -> bool) if status=True
        - single-worker mapping if workername specified and known
        - full workers mapping otherwise
    - If refresh=True and update_workers completes successfully, the application worker state may be updated (depends on application.update_workers implementation).
    - If update_workers raised, a 503 HTTPError is raised and the error is logged; no normal response body is written after the exception.

## Side Effects:
    - May trigger asynchronous work via await asyncio.wait(self.application.update_workers(workername=...)). The actual effect depends on the application's implementation of update_workers (commonly it refreshes the application.workers mapping and/or internal event state).
    - Logs an error message via logger.error(...) if the refresh operation raises an exception.
    - Writes to the HTTP response (via self.write), sending worker data back to the client.
    - Raises web.HTTPError which will be transformed into an HTTP error response by Tornado's error handling.

