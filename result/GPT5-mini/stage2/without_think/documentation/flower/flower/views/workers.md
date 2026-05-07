# `workers.py`

## `flower.views.workers.WorkerView` · *class*

## Summary:
Represents an HTTP GET request handler for a single worker's detail page. It attempts to refresh a specific worker's data, validates that the worker exists and contains runtime stats, and renders the "worker.html" template with the worker context.

## Description:
This Tornado request handler class is a thin controller for displaying details about one worker identified by name. It is invoked by Tornado when an incoming GET request is routed to the Worker handler with a worker name parameter (for example, GET /workers/<name>). WorkerView.get orchestrates a best-effort refresh of the worker's data, reads the worker record from the application state, performs simple validation (existence and presence of 'stats'), and then renders the "worker.html" template with the worker context.

Scenarios / callers:
- Tornado's routing/dispatcher: Tornado will instantiate handler objects and call the async get(self, name) method for GET requests targeted at the worker route.
- Tests and controller-level integrations that exercise handler behavior may call get(name) via Tornado's testing utilities or by simulating the HTTP request.

Motivation and responsibility boundary:
- Responsibility: present worker details to an HTTP client; ensure the worker exists and that stats are available before rendering.
- Not responsible for: populating workers data store in general — it delegates an on-demand refresh to self.application.update_workers(workername=name) but does not guarantee a refresh (see behavior notes).
- Error handling: swallows and logs exceptions from the refresh step to avoid turning worker-refresh faults into 500 errors; downstream rendering errors are left to Tornado's error handling.

## State:
Attributes accessed and their expected types:
- self.application
  - Type: application object provided by Tornado (concrete application type depends on the project)
  - Required attributes:
    - update_workers: callable update_workers(workername: str) -> Any
      - Expected behavior: refreshes or updates the application's workers mapping for the specified worker name. May be synchronous or asynchronous (see Behavior note).
    - workers: mapping-like object (dict-like)
      - Behavior: supports .get(name) and returns either a worker mapping/object or None.
- self.render
  - Type: callable provided by BaseHandler
  - Signature: render(template_name: str, **context) -> None (writes rendered template to HTTP response)
- module-level logger
  - Name: logger (referenced in the method)
  - Type: logging.Logger-like
  - Usage: logger.error(e) called when update_workers raises exceptions

Invariants:
- After successful completion (no HTTPError raised), the template "worker.html" must have been rendered with context containing a mapping equal to dict(worker, name=name).

For __init__:
- WorkerView does not define its own __init__; it inherits from BaseHandler. Instantiation follows Tornado's handler creation rules. No additional constructor arguments are required beyond what Tornado provides.

## Lifecycle:
Creation:
- Instantiation is managed by Tornado; typical creation requires Tornado to supply application, request, and other handler init args. Do not rely on directly instantiating the handler in application code; use Tornado's routing.

Usage sequence (typical):
1. Tornado receives GET /workers/<name>, routes to WorkerView.
2. Tornado constructs WorkerView instance (BaseHandler __init__ runs).
3. Tornado calls the asynchronous get(self, name) method on the instance.
4. get performs:
   - Attempted call to self.application.update_workers(workername=name) (exceptions logged, not re-raised).
   - Lookup worker = self.application.workers.get(name).
   - If lookup fails or worker lacks 'stats', raise tornado.web.HTTPError(404, <message>).
   - Otherwise call self.render("worker.html", worker=dict(worker, name=name)) to produce the response.
5. Tornado completes the request/response lifecycle and eventually disposes of the handler instance.

Sequencing constraints:
- get is an async method and decorated with @web.authenticated; Tornado will ensure authentication before invocation. The method itself does not await update_workers — implementers should be mindful of whether update_workers is synchronous or a coroutine.

Destruction / cleanup:
- WorkerView defines no cleanup logic (no close(), no context-manager behavior). Request lifecycle cleanup is handled by Tornado/BaseHandler. If update_workers triggers background I/O, its cleanup is the responsibility of the application-level code.

## Method Map:
Mermaid flowchart showing call dependencies and typical invocation order:

graph LR
    A[HTTP GET /workers/&lt;name&gt;] --> B[get(name)]
    B --> C[call application.update_workers(workername=name)]
    C -->|exception logged| D[logger.error(e)]
    B --> E[worker = application.workers.get(name)]
    E --> F{worker is None?}
    F -- Yes --> G[raise HTTPError(404, "Unknown worker '<name>'")]
    F -- No --> H{'stats' in worker?}
    H -- No --> I[raise HTTPError(404, "Unable to get stats for '<name>' worker")]
    H -- Yes --> J[render("worker.html", worker=dict(worker, name=name))]

## Raises:
- tornado.web.HTTPError(404, message)
  - Trigger: self.application.workers.get(name) returns None
  - Message: f"Unknown worker '{name}'"
- tornado.web.HTTPError(404, message)
  - Trigger: worker is not None but does not contain the 'stats' key
  - Message: f"Unable to get stats for '{name}' worker"
- Exceptions raised by self.render(...) or Tornado internals:
  - These are not caught here and will propagate to Tornado's error handlers (may result in 500s or custom error pages).
- Exceptions raised by self.application.update_workers(...):
  - These are caught by a broad except Exception as e and are logged via logger.error(e). They are not re-raised by this method.

## Behavior notes and edge cases:
- update_workers sync/async mismatch:
  - The source calls self.application.update_workers(workername=name) without awaiting. If update_workers is an async coroutine, the call will produce a coroutine object and will not perform the intended refresh. When reimplementing or integrating, ensure update_workers is synchronous or explicitly await it (and adjust the call accordingly).
- Worker object shape:
  - The method expects the worker returned from .get(name) to be mapping-like because it calls dict(worker, name=name) to construct the template context. If worker is not a mapping (or incompatible with dict(...)), TypeError will be raised by dict(...) and will propagate.
- Logging:
  - All exceptions from update_workers are logged with logger.error(e). No additional information is appended; if richer logging is required, wrap update_workers call at the application level or modify the handler to add context.
- Exact messages:
  - Tests or clients may assert on the exact HTTPError messages. Preserve the f-string message formats when reproducing behavior.

## Example:
Typical request flow (illustrative; Tornado instantiates and invokes handler):

1) Incoming request:
   - HTTP GET /workers/worker1 routed to WorkerView

2) Handler behavior (high-level):
   - WorkerView.get("worker1") is invoked.
   - The handler calls application.update_workers(workername="worker1") (exceptions logged).
   - The handler looks up worker = application.workers.get("worker1").
   - If worker is None -> HTTP 404 "Unknown worker 'worker1'".
   - If 'stats' not in worker -> HTTP 404 "Unable to get stats for 'worker1' worker".
   - Otherwise, the handler calls render("worker.html", worker=dict(worker, name="worker1")) to produce the HTTP response.

Notes for implementers:
- When reproducing this class, ensure BaseHandler provides render(...) and that the application object exposes update_workers(...) and a workers mapping. Respect the @web.authenticated decoration semantics (Tornado will guarantee authentication).

### `flower.views.workers.WorkerView.get` · *method*

## Summary:
Handle an HTTP GET request for a named worker: attempt a worker-data refresh, validate that the worker exists and contains 'stats', and render the "worker.html" template with the worker context; if validation fails, raise a 404 HTTP error.

## Description:
This asynchronous request handler method is invoked by the web framework (Tornado) when an HTTP GET request is routed to the Worker view for a specific worker name (for example, GET /workers/<name>). It performs a short controller workflow: request → optional data refresh → validation → render.

Why this is a separate method:
- Keeps the request-handling lifecycle clear and testable (refresh + validation + render).
- Encapsulates the error handling for the worker refresh step so failures there do not directly cause a 500; instead they are logged and the method still attempts to read existing worker data.

Known callers / invocation context:
- Tornado's request dispatcher calls this method when handling GET requests for the Worker handler route.
- Typical lifecycle stage: during an active HTTP request for the worker details page.

## Args:
    name (str)
        - Description: Worker identifier string extracted from the URL/routing layer.
        - Required: Yes (no default).
        - Expected values: non-empty string corresponding to a key in self.application.workers.

## Returns:
    None
    - This method does not return a Python value. Instead it produces an HTTP response by calling the handler's render method.
    - On success: the "worker.html" template is rendered and written to the HTTP response body with a template context equal to dict(worker, name=name).
    - On failure: raises tornado.web.HTTPError(404, <message>) (see Raises).

## Raises:
    tornado.web.HTTPError(404, message)
        - If no worker with the given name exists:
            * Condition: self.application.workers.get(name) returns None
            * Raised with message: f"Unknown worker '{name}'"
        - If the worker exists but does not contain a 'stats' key:
            * Condition: worker is not None and 'stats' not in worker
            * Raised with message: f"Unable to get stats for '{name}' worker"
    Any exception raised by render() or the web framework will propagate to the framework's error handlers.
    Note: Exceptions raised by self.application.update_workers(...) are caught in this method and are NOT re-raised; they are logged via logger.error(e).

## State Changes:
Attributes READ:
    - self.application.update_workers (the callable is invoked with workername=name)
    - self.application.workers (mapping/dict-like): accessed via .get(name) to obtain worker data
    - module-level logger variable named logger (used to log exceptions)

Attributes WRITTEN:
    - None of the handler's attributes are assigned or mutated in this method.
    - Side-effect: self.render(...) writes the rendered template to the HTTP response stream (mutates the request/response state managed by the handler/framework).
    - Note: calling self.application.update_workers(...) may mutate self.application.workers internally (this is an external/mutated state of application, not a direct assignment in this method).

## Constraints:
Preconditions (what must be true before calling):
    - self.application must be present and expose:
        * update_workers(workername=<str>) callable that can be invoked with the worker name as a keyword argument.
        * workers attribute that is a mapping-like object supporting .get(name).
    - The handler base class must provide a render(template_name: str, **context) method.
    - A module-level logger variable named logger should exist and be callable as logger.error(...). The source references logger (the exact definition is expected elsewhere in the module).
    - name should be a valid key name for the workers mapping.

Postconditions (what the method guarantees on success):
    - If execution completes without raising, the HTTP response will contain the rendered "worker.html" template with context worker=dict(worker, name=name).
    - If the worker is missing or lacks 'stats', a tornado.web.HTTPError(404, ...) will have been raised (so no template is rendered by this method).
    - Any exception from update_workers will be logged and will not prevent the lookup/render attempt.

## Side Effects:
    - Calls self.application.update_workers(workername=name): this may perform I/O or mutate application state (e.g., refresh the workers mapping). Those effects are external to this method.
    - Logs exceptions from update_workers using logger.error(e).
    - Reads from self.application.workers to retrieve the worker mapping for the given name.
    - Calls self.render("worker.html", worker=dict(worker, name=name)) which writes the rendered output to the HTTP response.

## Behavior details and edge cases (implementation guidance):
    - The method is declared async but does not await update_workers; it invokes update_workers synchronously. Therefore:
        * If update_workers is a synchronous function, it will execute before the lookup.
        * If update_workers is an async coroutine and is not awaited, invoking it will return a coroutine object and no refresh will occur. When reproducing this method, ensure callers and update_workers are consistent (either await update_workers or keep it synchronous).
    - Exceptions:
        * Exceptions raised by update_workers are caught with a broad except Exception as e and logged via logger.error(e); they do not change control flow beyond logging.
        * Exceptions from self.render(...) are not caught here and will propagate to Tornado's error handlers.
    - The worker object is assumed to be mapping-like. The code builds the template context by calling dict(worker, name=name). This will:
        * Create a shallow copy of worker with the 'name' key set/overwritten.
        * Raise TypeError if worker is not a mapping or is incompatible with dict() construction.
    - Exact HTTPError messages are built using f-strings and include the provided name; consumers/tests may assert on these exact message strings.
    - Implementation should keep string formatting and HTTP error codes identical to preserve client-facing behavior and tests.

## `flower.views.workers.WorkersView` · *class*

## Summary:
Represents the HTTP handler that returns the current set of Celery worker statistics to the web UI or as JSON. Handles GET requests, optional refresh of worker data, optional purging of offline workers, and rendering to a template or returning JSON.

## Description:
WorkersView is a Tornado RequestHandler subclass (via BaseHandler) used by the Flower web application to expose worker information to the web UI. It is invoked by an HTTP GET request to the workers endpoint. Typical callers are the Tornado application/router that maps an HTTP path (e.g., "/workers") to this handler; the handler method is executed by Tornado's request handling machinery.

Responsibilities and boundaries:
- Query the application events state (self.application.events.state) for recorded counters and worker objects.
- Optionally request an immediate refresh of workers from the application (self.application.update_workers()) when the HTTP parameter refresh is truthy.
- Merge counter-derived values and worker attribute information into a single per-worker dict.
- Optionally purge workers that are offline and whose last heartbeat exceeds a configured timeout (options.purge_offline_workers).
- Return the worker list as JSON when the query argument json is truthy; otherwise, render the "workers.html" template with the workers dictionary and broker/auto-refresh context.

This handler deliberately avoids directly mutating the application events state except by invoking update_workers(); it prepares view-layer data only.

## State:
This class defines no persistent instance attributes of its own in the provided source; it relies on BaseHandler and the Tornado request lifecycle. Relevant runtime state used by the methods:

- self.application: (object) Tornado application instance hosting this handler. The code expects:
  - self.application.events.state: container-like object with:
    - counter: an iterable mapping of worker names to counter/value dict-like objects.
    - workers: a mapping of worker name -> worker object. Worker objects are expected to have attributes used below.
  - self.application.update_workers: callable that triggers a state refresh of workers (may raise).
  - self.application.capp: an application-level Celery app with connection().as_uri() available for display.
  - self.application.options: object with auto_refresh boolean-like attribute.

- options.purge_offline_workers: (int or None) global configuration value. When None, no purging occurs; when an integer number of seconds, workers deemed offline longer than this threshold are removed from the presented result.

Worker object attributes referenced (may appear on worker objects):
- hostname (str)
- pid (int)
- freq (float or int)
- heartbeats (iterable of numeric timestamps)
- clock (numeric)
- active (int)
- processed (int)
- loadavg (iterable or numeric)
- sw_ident (str)
- sw_ver (str)
- sw_sys (str)
- alive (bool) — used as status flag

Class invariants:
- _as_dict returns a dict representation of a worker either by using worker._fields (if present) or by selecting a fixed subset of attributes in _info.
- get() will always produce a dictionary mapping worker name -> info dict (possibly empty if no matching workers) and then either write JSON or render template.

## Lifecycle:
Creation:
- Instantiated by Tornado when a matching HTTP request arrives. No explicit constructor arguments are required beyond the standard Tornado RequestHandler arguments (application, request, etc.) provided by Tornado.

Usage (typical sequence):
1. Tornado creates the handler instance for an incoming GET request.
2. Tornado calls the asynchronous get() method:
   - The method is decorated with @web.authenticated, so Tornado ensures a logged-in context before execution.
   - It reads query arguments 'refresh' and 'json' via self.get_argument.
   - It accesses the application events state: events = self.application.events.state.
   - If refresh is true, it calls self.application.update_workers() inside a try/except and logs exceptions (the exception is caught and not propagated).
   - It iterates events.counter and, for each worker name also found in events.workers, builds an info dict by combining the counter values, worker attributes (via _as_dict), and a status field set from worker.alive.
   - If options.purge_offline_workers is not None, it computes current time and removes workers that are offline (status False) and whose latest heartbeat is absent or older than options.purge_offline_workers seconds.
   - If json is true, it writes a JSON-like dict with key "data" and value list(workers.values()) via self.write(); otherwise it renders the "workers.html" template with the workers dict, the broker URI (self.application.capp.connection().as_uri()), and autorefresh flag taken from self.application.options.auto_refresh.

Destruction:
- No explicit cleanup is required by this handler. Tornado will discard the handler instance after request completion. There are no open resources created by this class that require manual closing.

## Method Map:
flowchart LR
    GET[get()] --> GetArgs[get_argument('refresh','json')]
    GET --> EventsAccess[self.application.events.state]
    GET --> MaybeRefresh{if refresh}
    MaybeRefresh -->|true| Update[self.application.update_workers()]
    Update -->|exceptions caught| Log[logger.exception(...)]
    GET --> IterateCounters[for name, values in events.counter.items()]
    IterateCounters --> WorkerLookup[events.workers[name]]
    WorkerLookup --> BuildInfo[info = dict(values); info.update(_as_dict); info.update(status=worker.alive)]
    BuildInfo --> WorkersDict[workers[name] = info]
    GET --> PurgeCheck{if options.purge_offline_workers is not None}
    PurgeCheck --> ComputeTimestamp[time.time()]
    PurgeCheck --> IdentifyOffline[computes last_heartbeat and compares to threshold]
    IdentifyOffline --> RemoveOffline[workers.pop(name)]
    GET --> Output{if json}
    Output -->|true| Write[self.write({'data': list(workers.values())})]
    Output -->|false| Render[self.render("workers.html", ...)]

## Methods and behavior details (reimplementation guidance):
- async def get(self):
  - Inputs:
    - HTTP request context; reads two query arguments:
      - 'refresh': default False, type=bool
      - 'json': default False, type=bool
    - It expects the handler to have a valid self.application with the attributes described above.
  - Behavior:
    - Read query args.
    - Obtain events = self.application.events.state.
    - If refresh is true:
      - Call self.application.update_workers() inside try/except Exception as e.
      - If an exception occurs in update_workers(), call logger.exception('Failed to update workers: %s', e) and continue (do not re-raise).
    - Create an initially empty dict workers.
    - For each (name, values) in events.counter.items():
      - If name not in events.workers, skip that entry.
      - Let worker = events.workers[name].
      - info = dict(values)  (creates a shallow copy of the counter values)
      - info.update(self._as_dict(worker))  (merge attribute-based info)
      - info.update(status=worker.alive)
      - workers[name] = info
    - If options.purge_offline_workers is not None:
      - timestamp = int(time.time())
      - Build offline_workers = []
      - For each (name, info) in workers.items():
        - If info.get('status', True) is truthy, skip (worker is online or default to True).
        - heartbeats = info.get('heartbeats', []) — expects an iterable of timestamps (numeric).
        - last_heartbeat = int(max(heartbeats)) if heartbeats else None
        - If not last_heartbeat or timestamp - last_heartbeat > options.purge_offline_workers:
          - append name to offline_workers
      - For each name in offline_workers: workers.pop(name)
    - If json is true:
      - Call self.write(dict(data=list(workers.values()))) — rely on Tornado's write to serialize dict to JSON if handler is configured to do so.
    - Otherwise:
      - Call self.render("workers.html", workers=workers, broker=self.application.capp.connection().as_uri(), autorefresh=1 if self.application.options.auto_refresh else 0)
  - Edge cases and constraints:
    - If events.counter or events.workers is missing or not mapping-like, KeyError/AttributeError may occur. The handler does not catch these and they will propagate to Tornado's error handling.
    - update_workers() exceptions are caught and logged; no retry is attempted.
    - If worker objects do not have .alive attribute, an AttributeError will occur when assigning status=worker.alive.
    - heartbeats values must be comparable by max(); if heartbeats contains non-comparable types, max() will raise an error.
    - options.purge_offline_workers may be zero or negative. The code compares timestamps numerically; a non-positive threshold effectively purges any offline worker with no recent heartbeat accordingly.
  - Returns:
    - No explicit return value; method responds to the HTTP client by calling self.write() or self.render().

- @classmethod def _as_dict(cls, worker):
  - Purpose: produce a dictionary representation of a worker instance.
  - Behavior:
    - If the worker has attribute _fields, treat it as an iterable of field names and return a dict mapping each field name k to getattr(worker, k).
    - Otherwise, call and return cls._info(worker).

- @classmethod def _info(cls, worker):
  - Purpose: defensive helper that extracts a fixed subset of attributes from a worker into a dict.
  - _fields tuple:
    ('hostname', 'pid', 'freq', 'heartbeats', 'clock',
     'active', 'processed', 'loadavg', 'sw_ident',
     'sw_ver', 'sw_sys')
  - Behavior:
    - Iterates these keys, gets each attribute value via getattr(worker, key, None).
    - Yields (key, value) only when value is not None.
    - Returns dict of the yielded key/value pairs.

## Raises:
- The implementation itself catches exceptions from update_workers() and logs them instead of re-raising.
- The following exceptions may occur and propagate (not handled by this handler):
  - AttributeError or KeyError if expected attributes on self.application, events, worker objects, or options are missing or malformed.
  - TypeError/ValueError from self.get_argument if Tornado's conversion to bool fails or the argument is malformed (behavior depends on Tornado's RequestHandler).
  - Exceptions from self.write() or self.render() if template rendering or response serialization fails.
  - Exceptions from time.time(), max(heartbeats) if heartbeats is empty or contains invalid items; code guards empty heartbeats by checking truthiness, but max() can throw if heartbeats contains incompatible values.

## Example (textual):
- A browser requests GET /workers?refresh=1&json=1 with an authenticated session:
  - Tornado instantiates WorkersView and calls get(); refresh is True, json is True.
  - The handler calls application.update_workers() (exceptions logged).
  - It aggregates counters and worker attributes into worker info dicts.
  - It applies purge logic if options.purge_offline_workers is set.
  - The handler responds with JSON: {"data": [ {worker1_info}, {worker2_info}, ... ] }.

- A browser requests GET /workers (no json):
  - The handler prepares the same workers dict and calls render("workers.html", workers=..., broker=..., autorefresh=...), producing an HTML page showing workers.

Notes:
- The handler requires Tornado authentication via the @web.authenticated decorator to be meaningful; ensure Tornado is configured with a login URL and authentication logic for this decorator to enforce access control.
- Because this handler relies heavily on the shape of self.application.events.state and worker objects, ensure those objects expose the expected mappings and attributes when reimplementing.

### `flower.views.workers.WorkersView.get` · *method*

## Summary:
Handles an HTTP GET request that returns the current set of worker summaries (either JSON or an HTML page). It optionally triggers a workers refresh, merges runtime event counters with live worker state, filters out stale/offline workers based on configured purge settings, and writes or renders the resulting worker list to the response.

## Description:
- Known callers / invocation context:
    - Invoked by the Tornado web framework as the GET handler for the WorkersView endpoint (i.e., when an HTTP GET request is routed to WorkersView). This method runs as part of handling an incoming HTTP GET request in the request/response lifecycle.
- Why this logic is its own method:
    - It encapsulates the full request-handling flow for the workers listing: reading request arguments, optionally refreshing worker state, composing the combined worker payload from event counters and live worker entries, applying purge logic for offline workers, and producing the final HTTP response in either JSON or HTML. Separating this behavior into a single method keeps the HTTP handling logic cohesive and consistent with Tornado's RequestHandler lifecycle.

## Args:
This method does not accept positional parameters; it relies on HTTP query arguments accessible via the handler API:
- refresh (bool)
    - Source: request query parameter named "refresh".
    - Allowed values: True or False.
    - Default: False.
    - Effect: When True, attempts to call the application-level update_workers() to refresh the worker list before composing the response.
- json (bool)
    - Source: request query parameter named "json".
    - Allowed values: True or False.
    - Default: False.
    - Effect: When True, the method returns a JSON response containing the list of workers; when False, it renders the "workers.html" template.

Notes on parsing:
- Both arguments are read via self.get_argument(..., type=bool) and therefore are interpreted as booleans by Tornado's argument parsing.

## Returns:
- None (no return value). The method produces an HTTP response as a side effect:
    - If json is True: writes a JSON object { "data": [ ... ] } where each element is a worker info dict.
    - If json is False: renders the "workers.html" template with context:
        - workers: mapping name -> info dict
        - broker: broker URI obtained from self.application.capp.connection().as_uri()
        - autorefresh: 1 if self.application.options.auto_refresh truthy, else 0

Edge-case return behavior:
- If there are no workers, the JSON response is { "data": [] } or the rendered template receives an empty mapping for workers.

## Raises:
- The method does not explicitly re-raise exceptions from update_workers (exceptions from update_workers are caught and logged).
- Unhandled exceptions can propagate from any of the called functions/methods (for example, self._as_dict, events.counter iteration, self.render or self.write, or application.capp.connection().as_uri()). There is no additional exception wrapping in this method.

## State Changes:
Attributes READ:
- self.application
    - self.application.events.state (used as events)
    - self.application.update_workers() (may be called)
    - self.application.capp.connection().as_uri() (used to populate broker in template)
    - self.application.options.auto_refresh (checked when rendering)
- self._as_dict(worker) (calls a handler instance method to obtain worker-specific dict data)
- self.get_argument(...) (reads request query args)
- self.write(...) or self.render(...) (Tornado response helpers are invoked)
- module-level options (options.purge_offline_workers is read)

Attributes WRITTEN:
- No persistent attributes of self are modified by this method. All work is performed in local variables; final output is produced via HTTP response methods (self.write / self.render).

## Constraints:
Preconditions:
- self.application must be a valid application object exposing:
    - events.state with attributes:
        - counter: an iterable mapping of worker_name -> counter-values (iterated as items())
        - workers: a mapping of worker_name -> worker-object
    - capp with connection().as_uri() callable to obtain the broker URI
    - options with an auto_refresh attribute (accessed as self.application.options.auto_refresh)
- events.counter items must be iterable as (name, values) pairs; values must be convertible to dict via dict(values).
- Each referenced worker object in events.workers must be suitable for:
    - self._as_dict(worker) to produce a dict of worker properties
    - having an attribute alive that indicates online status
- options.purge_offline_workers must be either None or an integer number of seconds; if integer, it controls how old a last heartbeat must be before purging offline workers.
- Request arguments "refresh" and "json" must be parseable by Tornado as booleans when passed to get_argument(..., type=bool).

Postconditions:
- An HTTP response has been produced (via self.write or self.render).
- The response contains a composed snapshot of current workers filtered by the optional purge policy; the handler does not mutate persistent worker state directly (only may trigger application.update_workers()).

## Side Effects:
- May call self.application.update_workers() if refresh is True. Exceptions from this call are caught and logged (logger.exception).
- Reads global/module-level configuration options.purge_offline_workers and may drop offline workers from the returned list based on heartbeat timestamps.
- Calls self._as_dict(worker) for each worker (delegates serialization concerns to that helper).
- Calls application-level code to obtain broker URI: self.application.capp.connection().as_uri().
- Produces network I/O via the HTTP response:
    - If json is True: performs self.write(dict(data=...)) which sends JSON to the client.
    - If json is False: invokes self.render("workers.html", ...) which renders HTML and sends it to the client.
- Logs an exception if update_workers() raises.
- No persistent mutation of self attributes; local variable workers is mutated and used to build the response.

## Implementation notes / algorithm summary (helpful to reimplement):
1. Parse boolean query args 'refresh' and 'json' (default False).
2. Obtain events state from self.application.events.state.
3. If refresh requested: attempt to call self.application.update_workers(); on exception log and continue.
4. Build an initially empty dict workers.
5. For each (name, values) in events.counter.items():
    - Skip entries whose name is not a key in events.workers.
    - Take worker = events.workers[name].
    - Start with info = dict(values) (copy the counter values).
    - Merge info.update(self._as_dict(worker)).
    - Set info['status'] = worker.alive.
    - Assign workers[name] = info.
6. If options.purge_offline_workers is not None:
    - Compute timestamp = int(time.time()).
    - For each worker entry with status False (offline), obtain heartbeats = info.get('heartbeats', []).
    - Determine last_heartbeat = int(max(heartbeats)) if heartbeats else None.
    - If last_heartbeat is falsy (None) OR timestamp - last_heartbeat > options.purge_offline_workers, mark worker for removal.
    - Remove marked workers from the workers mapping.
7. If json argument true: respond with JSON object dict(data=list(workers.values())).
   Else: render "workers.html" with context:
    - workers (the mapping)
    - broker = self.application.capp.connection().as_uri()
    - autorefresh = 1 if self.application.options.auto_refresh else 0

### `flower.views.workers.WorkersView._as_dict` · *method*

## Summary:
Convert a worker object into a plain dictionary of its fields and values for presentation, preserving attribute values when the worker exposes a _fields sequence and falling back to a filtered attribute list otherwise. This operation does not mutate the view instance or the worker.

## Description:
- Known callers:
  - WorkersView.get: invoked while building the per-worker info map during the HTTP GET handler that returns either JSON or renders the workers.html template. The call site uses the returned mapping to merge with event counters and status information before rendering or returning JSON.
- Invocation context:
  - Called at request-time as part of presenting worker state to users (rendering the UI or returning the JSON payload). This is a presentation/data-shaping helper used in the request lifecycle.
- Why this is a separate method:
  - Encapsulates the logic for converting different kinds of worker objects (e.g., namedtuple-like objects exposing _fields vs plain objects with known attributes) into a uniform dict representation.
  - Keeps the GET handler concise and isolates conversion behavior so it can be reused, tested independently, and overridden by subclasses if necessary.

## Args:
    cls (type): The WorkersView class (method is a classmethod). Not used for state mutation; used only to call cls._info when needed.
    worker (object): Any object representing a worker. Allowed shapes:
        - Objects that expose a _fields attribute (typically a sequence/iterable of field names). For this branch, each name in worker._fields must be a valid attribute name on worker.
        - Objects without _fields but with attributes named by the _info method's _fields tuple (hostname, pid, freq, heartbeats, clock, active, processed, loadavg, sw_ident, sw_ver, sw_sys). Attributes may be missing; _info will skip attributes with value None.

## Returns:
    dict: A mapping of field name -> value representing the worker.
    - If worker has a _fields attribute: returns a dict containing each name in worker._fields mapped to getattr(worker, name). Values may be None; missing attributes will raise AttributeError (see Raises).
    - Otherwise: returns the dict produced by cls._info(worker), which yields only attributes whose getattr(..., None) is not None (i.e., _info filters out None-valued or absent attributes).

## Raises:
    AttributeError: If worker has a _fields attribute but one of the names listed in worker._fields is not an attribute of worker (getattr without default is used).
    TypeError: If worker._fields exists but is not iterable or contains non-hashable field names that cannot be used as dict keys.
    Any exception raised by cls._info(worker) will propagate (e.g., if cls._info is modified to raise).

## State Changes:
- Attributes READ:
    - None of the view instance's attributes (no self.<attr>) are read or modified. The method does call cls._info (a class attribute/method), but it does not read or mutate persistent view state.
- Attributes WRITTEN:
    - None. The method does not modify any attributes on self/cls.
- Note: The method reads attributes from the provided worker object (either via worker._fields and getattr(worker, k) or via getattr(worker, key, None) inside _info), but those are not view attributes and are not modified.

## Constraints:
- Preconditions:
    - worker must be a Python object.
    - If worker exposes _fields:
        - worker._fields must be an iterable of strings (or objects convertible to dict keys) corresponding to attribute names present on worker.
    - If worker does not expose _fields:
        - Attributes listed in WorkersView._info._fields may be present; missing attributes are acceptable because _info uses getattr(..., None) and filters out None.
- Postconditions:
    - The return value is a dict describing the worker suitable for merging with other worker metadata (e.g., event counters).
    - No mutations to worker or view/handler state occur.

## Side Effects:
- None external: no I/O, no network, no logging, and no external service calls are performed by this method itself.
- Internal: only attribute reads on the provided worker object and a call to cls._info when _fields is absent.

## Implementation notes / behavior differences to be aware of:
- Two code paths with different semantics:
    1. worker has _fields: strict mapping — each name in _fields is fetched with getattr(worker, name) (no default). Missing attributes will raise AttributeError; None values are preserved in the result.
    2. worker lacks _fields: cls._info is used, which obtains values with getattr(worker, key, None) and then filters out keys whose value is None (so absent attributes or attributes equal to None are omitted).
- Because the two branches behave differently with respect to missing attributes and None values, callers that rely on the presence/absence of keys should account for this difference.

### `flower.views.workers.WorkersView._info` · *method*

## Summary:
Return a serializable dictionary of well-known worker attributes by reading a predefined set of fields from the provided worker object and excluding any fields with value None.

## Description:
This helper extracts a fixed list of attributes from a worker-like object and returns them as a plain dict of key -> value pairs for attributes that exist and are not None. The first parameter is named `cls` in the implementation but is unused by the function; the function operates solely on the second parameter, `worker`.

Typical usage context:
- Called wherever code needs a compact, JSON-friendly representation of a worker's runtime attributes (for example, preparing response data for a web endpoint that lists or describes workers). This function is intentionally separated as a small utility to centralize the list of fields to expose and to keep formatting logic out of request handlers or templates.

Why this is a separate method:
- Encapsulates the canonical set of worker attributes to be exposed.
- Keeps worker-to-dict conversion logic in one place (easy to update the exposed fields).
- Avoids duplicating the filtering (omit None) logic across multiple callers.

## Args:
    cls (type): The class object when used as a classmethod; the function does not read or modify this argument.
    worker (object): Any object representing a worker. The function will attempt to read the following attribute names from this object (if present): 'hostname', 'pid', 'freq', 'heartbeats', 'clock', 'active', 'processed', 'loadavg', 'sw_ident', 'sw_ver', 'sw_sys'.
        - Allowed values: attributes may be of any type. Attributes with the value None are omitted from the result.
        - If an attribute is absent, it is treated as None (and therefore omitted), because getattr is called with a default of None.

## Returns:
    dict[str, Any]: A dictionary mapping each attribute name (from the canonical list) to the corresponding non-None attribute value from `worker`.
    - If none of the listed attributes are present or all values are None, returns an empty dict.
    - Keys always come from the predefined field list; no other keys are produced.
    - Ordering: the returned dict preserves the iteration order of the _fields tuple (in modern Python versions dict preserves insertion order).

## Raises:
    - The function itself does not explicitly raise exceptions for missing attributes because getattr(worker, key, None) is used. Therefore no exceptions are raised in the normal case.
    - However, attribute access may invoke property getters or descriptors on `worker`; any exception raised by those getters (AttributeError, custom exceptions, or other runtime errors) will propagate out of this function unchanged.

## State Changes:
    Attributes READ:
        - None on self/cls (the function does not access or depend on any self.<attr>).
    Attributes WRITTEN:
        - None (the function does not mutate `cls`, `worker`, or any external state).

## Constraints:
    Preconditions:
        - `worker` must be an object; its attributes (if present) should be safe to read. If attribute access has side effects or raises, those behaviors will take effect.
        - The function expects no particular type beyond supporting attribute access via getattr.

    Postconditions:
        - The returned dictionary contains zero or more of the canonical field names mapped to their non-None values from `worker`.
        - No attribute on `worker` or any external state is modified by this call.

## Side Effects:
    - No I/O or external service calls are performed by this function.
    - The only observable effects are attribute reads on `worker`. If those attribute accesses have side effects (e.g., lazy-loading, logging, raising exceptions), those side effects will occur.

